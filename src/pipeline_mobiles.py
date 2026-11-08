"""Ingestion pipeline for Mobile Phones from Amazon Reviews 2023 (McAuley Lab / UCSD).

Extracts genuine smartphones and cell phones from the Cell_Phones_and_Accessories dataset,
streams matching customer reviews, and additively ingests them into PostgreSQL.
"""

import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import DATA_DIR, FINAL_PRODUCT_COLUMNS, FINAL_REVIEW_COLUMNS
from src.data_cleaner import clean_reviews, extract_primary_image_url, format_category_hierarchy
from src.db.connection import SessionLocal
from src.db.models import Product, Review

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

META_PARQUET_PATH = DATA_DIR / "meta_mobiles_shard0.parquet"
REVIEW_STREAM_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/Cell_Phones_and_Accessories.jsonl"
)
OUTPUT_PRODUCTS_CSV = DATA_DIR / "mobiles_products.csv"
OUTPUT_REVIEWS_CSV = DATA_DIR / "mobiles_reviews.csv"

# Target parameters
TARGET_MOBILE_REVIEWS = 2500
MAX_SCAN_LINES = 500000


def is_cell_phone_category(cats) -> bool:
    """Check if categories hierarchy includes mobile phone subcategories."""
    if cats is None:
        return False
    c_list = [str(c).strip() for c in (list(cats) if isinstance(cats, (list, tuple, np.ndarray)) else [])]
    return any(
        c in [
            "Cell Phones",
            "Carrier Cell Phones",
            "Unlocked Cell Phones",
            "Prepaid Cell Phones",
            "Refurbished & Used Cell Phones",
        ]
        for c in c_list
    )


def extract_genuine_mobiles(parquet_path: Path = META_PARQUET_PATH) -> pd.DataFrame:
    """Extract strictly genuine cell phones / smartphones from the metadata shard."""
    logger.info("Reading mobile phone metadata from %s...", parquet_path)
    t0 = time.time()
    table = pq.read_table(
        parquet_path,
        columns=[
            "parent_asin",
            "title",
            "main_category",
            "categories",
            "price",
            "store",
            "images",
            "average_rating",
            "rating_number",
        ],
    )
    df = table.to_pandas()
    logger.info("Loaded %d raw catalog entries in %.2fs", len(df), time.time() - t0)

    # 1. Category validation
    has_cat = df["categories"].apply(is_cell_phone_category)

    # 2. Strict accessory exclusion to guarantee zero phone cases, cables, or protectors
    accessory_words = [
        "case", "cover", "screen protector", "cable", "cord", "charger",
        "holster", "mount", "holder", "adapter", "battery replacement",
        "skin", "pouch", "sleeve", "armband", "tempered glass", "lens protector",
        "wallet", "kickstand", "stylus", "ring holder", "tripod", "gimbal", "car mount",
        "replacement part", "replacement screen", "glass lens", "back glass", "housing",
        "sim card tray", "flex cable", "charging port replacement"
    ]
    title_lower = df["title"].astype(str).str.lower()
    not_acc = ~title_lower.apply(lambda t: any(w in t for w in accessory_words))

    # 3. Filter
    mobiles_df = df[has_cat & not_acc].copy()
    mobiles_df = mobiles_df.dropna(subset=["parent_asin", "title"])
    mobiles_df = mobiles_df.drop_duplicates(subset=["parent_asin"])

    # 4. Normalize and clean columns conforming to FINAL_PRODUCT_COLUMNS
    mobiles_df["product_id"] = mobiles_df["parent_asin"].astype(str).str.strip()
    mobiles_df["product_name"] = mobiles_df["title"].astype(str).str.strip()
    mobiles_df["main_category"] = "Cell Phones & Accessories"
    mobiles_df["categories_hierarchy"] = mobiles_df["categories"].apply(format_category_hierarchy)

    # Clean price
    def clean_price_val(p):
        if p is None or str(p).lower() in ("none", "nan", ""):
            return ""
        p_str = str(p).replace("$", "").replace(",", "").strip()
        try:
            return f"{float(p_str):.2f}"
        except ValueError:
            return ""

    mobiles_df["price"] = mobiles_df["price"].apply(clean_price_val)

    # Clean brand
    def clean_brand(store, title):
        if store and str(store).strip() not in ("Unknown", "None", "nan", ""):
            s = str(store).strip()
            if s.lower() != "generic":
                return s
        # Try inferring brand from title
        t = str(title).lower()
        for b in ["Samsung", "Apple", "Google", "Motorola", "OnePlus", "Xiaomi", "LG", "Nokia", "BLU", "Huawei", "Sony", "ZTE", "Alcatel", "Ulefone", "UMIDIGI", "Blackview", "ASUS"]:
            if b.lower() in t:
                return b
        return str(store).strip() if store else "Unknown"

    mobiles_df["brand"] = [clean_brand(s, t) for s, t in zip(mobiles_df["store"], mobiles_df["title"])]
    mobiles_df["image_url"] = mobiles_df["images"].apply(extract_primary_image_url)
    mobiles_df["average_rating"] = pd.to_numeric(mobiles_df["average_rating"], errors="coerce")
    mobiles_df["rating_number"] = pd.to_numeric(mobiles_df["rating_number"], errors="coerce").fillna(0).astype(int)

    clean_mobiles = mobiles_df[FINAL_PRODUCT_COLUMNS].reset_index(drop=True)
    logger.info("Extracted %d genuine mobile phones in %.2fs", len(clean_mobiles), time.time() - t0)
    return clean_mobiles


def stream_mobile_reviews(
    valid_asins: Set[str],
    target_count: int = TARGET_MOBILE_REVIEWS,
    max_scan_lines: int = MAX_SCAN_LINES,
) -> List[Dict]:
    """Stream customer reviews incrementally matching mobile phone ASINs."""
    logger.info(
        "Connecting to review stream for %d mobile phone ASINs (Target: %d reviews)...",
        len(valid_asins),
        target_count,
    )
    t0 = time.time()
    collected = []
    scanned_lines = 0

    with requests.get(REVIEW_STREAM_URL, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            scanned_lines += 1
            record = json.loads(line)
            asin = record.get("parent_asin")

            if asin in valid_asins:
                collected.append(record)
                if len(collected) % 250 == 0:
                    logger.info(
                        "Stream progress: %d reviews collected (scanned %d lines in %.1fs)...",
                        len(collected),
                        scanned_lines,
                        time.time() - t0,
                    )
                if len(collected) >= target_count:
                    logger.info("Reached target review count of %d!", target_count)
                    break

            if scanned_lines >= max_scan_lines:
                logger.info("Reached max scan limit of %d lines.", max_scan_lines)
                break

    logger.info(
        "Review stream finished: %d raw reviews collected from %d scanned lines in %.1fs",
        len(collected),
        scanned_lines,
        time.time() - t0,
    )
    return collected


def ingest_mobiles_to_database(
    products_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
    batch_size: int = 500,
) -> Dict[str, int]:
    """Insert mobile products and reviews additively using ON CONFLICT DO NOTHING."""
    logger.info("Beginning additive database ingestion...")
    t0 = time.time()

    # Prepare product dictionaries
    prod_records = []
    for _, row in products_df.iterrows():
        p_price = float(row["price"]) if row["price"] and str(row["price"]).strip() != "" else None
        p_avg = float(row["average_rating"]) if pd.notnull(row["average_rating"]) else None
        prod_records.append(
            {
                "product_id": str(row["product_id"]).strip(),
                "product_name": str(row["product_name"]).strip(),
                "main_category": str(row["main_category"]).strip(),
                "categories_hierarchy": str(row["categories_hierarchy"]).strip() or None,
                "price": p_price,
                "brand": str(row["brand"]).strip() or None,
                "image_url": str(row["image_url"]).strip() or None,
                "average_rating": p_avg,
                "rating_number": int(row["rating_number"]) if pd.notnull(row["rating_number"]) else 0,
            }
        )

    # Prepare review dictionaries
    rev_records = []
    for _, row in reviews_df.iterrows():
        rev_records.append(
            {
                "product_id": str(row["product_id"]).strip(),
                "user_id": str(row["user_id"]).strip() or None,
                "review_title": str(row["review_title"]).strip() or None,
                "review_text": str(row["review_text"]).strip(),
                "star_rating": float(row["star_rating"]),
                "review_timestamp": int(row["review_timestamp"]),
                "review_date": str(row["review_date"]),
                "helpful_votes": int(row["helpful_votes"]),
                "verified_purchase": bool(row["verified_purchase"]),
            }
        )

    session: Session = SessionLocal()
    products_inserted = 0
    reviews_inserted = 0

    try:
        session.begin()

        # 1. Insert products with ON CONFLICT (product_id) DO NOTHING
        logger.info("Ingesting %d mobile products in batches of %d...", len(prod_records), batch_size)
        for i in range(0, len(prod_records), batch_size):
            batch = prod_records[i : i + batch_size]
            stmt = insert(Product).values(batch).on_conflict_do_nothing(index_elements=["product_id"])
            res = session.execute(stmt)
            products_inserted += res.rowcount or len(batch)

        # 2. Insert reviews with ON CONFLICT uq_reviews_product_user_timestamp DO NOTHING
        logger.info("Ingesting %d mobile reviews in batches of %d...", len(rev_records), batch_size)
        for i in range(0, len(rev_records), batch_size):
            batch = rev_records[i : i + batch_size]
            stmt = insert(Review).values(batch).on_conflict_do_nothing(
                constraint="uq_reviews_product_user_timestamp"
            )
            res = session.execute(stmt)
            reviews_inserted += res.rowcount or len(batch)

        session.commit()
        logger.info("Transaction committed successfully in %.2fs!", time.time() - t0)

    except Exception as exc:
        session.rollback()
        logger.error("Ingestion failed and rolled back: %s", exc)
        raise
    finally:
        session.close()

    return {
        "products_submitted": len(prod_records),
        "reviews_submitted": len(rev_records),
    }


def run_mobile_pipeline():
    """Execute complete mobile ingestion pipeline."""
    print("=" * 70)
    print("AMAZON REVIEWS 2023: MOBILE PHONES DATASET INGESTION")
    print("Source: McAuley Lab / UC San Diego (Cell_Phones_and_Accessories)")
    print("=" * 70)

    # 1. Extract genuine mobile phones
    mobiles_df = extract_genuine_mobiles(META_PARQUET_PATH)
    valid_asins = set(mobiles_df["product_id"].unique())

    # 2. Stream reviews
    raw_reviews = stream_mobile_reviews(valid_asins, target_count=TARGET_MOBILE_REVIEWS, max_scan_lines=MAX_SCAN_LINES)

    # 3. Clean reviews
    clean_reviews_df = clean_reviews(raw_reviews)

    # 4. Save CSV artifacts
    logger.info("Saving mobile products CSV to %s...", OUTPUT_PRODUCTS_CSV)
    mobiles_df.to_csv(OUTPUT_PRODUCTS_CSV, index=False, encoding="utf-8")

    logger.info("Saving mobile reviews CSV to %s...", OUTPUT_REVIEWS_CSV)
    clean_reviews_df.to_csv(OUTPUT_REVIEWS_CSV, index=False, encoding="utf-8")

    # 5. Additive Ingestion into PostgreSQL
    db_stats = ingest_mobiles_to_database(mobiles_df, clean_reviews_df)

    print("\n" + "=" * 70)
    print("MOBILE INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"  * Mobile Phone Catalog Items : {len(mobiles_df):,}")
    print(f"  * Clean Customer Reviews     : {len(clean_reviews_df):,}")
    print(f"  * Average Mobile Star Rating : {clean_reviews_df['star_rating'].mean():.2f} / 5.0")
    print(f"  * Verified Purchase Rate     : {(clean_reviews_df['verified_purchase'].sum() / len(clean_reviews_df)) * 100:.1f}%")
    print(f"  * Products CSV Export        : {OUTPUT_PRODUCTS_CSV.name}")
    print(f"  * Reviews CSV Export         : {OUTPUT_REVIEWS_CSV.name}")
    print("=" * 70)


if __name__ == "__main__":
    run_mobile_pipeline()

