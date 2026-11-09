"""Seed all dataset files (general, mobiles, laptops) into PostgreSQL idempotently."""

import csv
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.db.connection import engine, SessionLocal
from src.db.models import Base, Product, Review
from src.config import DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def parse_products_file(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.exists():
        logger.warning("Products CSV not found: %s", file_path)
        return []

    products = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_price = row.get("price", "").strip()
            price_val = float(raw_price) if raw_price and raw_price.lower() != "nan" else None

            raw_avg = row.get("average_rating", "").strip()
            avg_rating = float(raw_avg) if raw_avg and raw_avg.lower() != "nan" else None

            raw_num = row.get("rating_number", "").strip()
            rating_num = int(raw_num) if raw_num and raw_num.isdigit() else 0

            products.append({
                "product_id": row["product_id"].strip(),
                "product_name": row["product_name"].strip(),
                "main_category": row.get("main_category", "").strip() or None,
                "categories_hierarchy": row.get("categories_hierarchy", "").strip() or None,
                "price": price_val,
                "brand": row.get("brand", "").strip() or None,
                "image_url": row.get("image_url", "").strip() or None,
                "average_rating": avg_rating,
                "rating_number": rating_num,
            })
    return products


def parse_reviews_file(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.exists():
        logger.warning("Reviews CSV not found: %s", file_path)
        return []

    reviews = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_helpful = row.get("helpful_votes", "").strip()
            helpful = int(raw_helpful) if raw_helpful and raw_helpful.isdigit() else 0

            verified = str(row.get("verified_purchase", "")).strip().lower() in ("true", "1")

            date_str = row.get("review_date", "").strip()
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                dt = datetime.utcnow()

            reviews.append({
                "product_id": row["product_id"].strip(),
                "user_id": row.get("user_id", "").strip() or None,
                "review_title": row.get("review_title", "").strip() or None,
                "review_text": row.get("review_text", ""),
                "star_rating": float(row["star_rating"]),
                "review_timestamp": int(row["review_timestamp"]),
                "review_date": dt,
                "helpful_votes": helpful,
                "verified_purchase": verified,
            })
    return reviews


def seed_database(batch_size: int = 1000) -> Dict[str, int]:
    """Ensure tables exist and seed all CSV datasets idempotently."""
    logger.info("Initializing schema...")
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()
    try:
        current_products = session.scalar(select(func.count(Product.product_id)))
        if current_products and current_products > 0:
            current_reviews = session.scalar(select(func.count(Review.review_id)))
            logger.info("Database already seeded: %d products, %d reviews", current_products, current_reviews)
            return {"products": current_products, "reviews": current_reviews}

        logger.info("Database is empty. Beginning full seed from CSV files...")
        start_time = time.time()

        product_files = [
            DATA_DIR / "products.csv",
            DATA_DIR / "mobiles_products.csv",
            DATA_DIR / "laptops_products.csv",
        ]
        review_files = [
            DATA_DIR / "reviews.csv",
            DATA_DIR / "mobiles_reviews.csv",
            DATA_DIR / "laptops_reviews.csv",
        ]

        # 1. Products
        for pfile in product_files:
            p_data = parse_products_file(pfile)
            for i in range(0, len(p_data), batch_size):
                batch = p_data[i : i + batch_size]
                stmt = insert(Product).values(batch).on_conflict_do_nothing(index_elements=["product_id"])
                session.execute(stmt)
                session.commit()
            logger.info("Processed product file: %s", pfile.name)

        # 2. Reviews
        for rfile in review_files:
            r_data = parse_reviews_file(rfile)
            for i in range(0, len(r_data), batch_size):
                batch = r_data[i : i + batch_size]
                stmt = insert(Review).values(batch).on_conflict_do_nothing(
                    index_elements=["product_id", "user_id", "review_timestamp"]
                )
                session.execute(stmt)
                session.commit()
            logger.info("Processed review file: %s", rfile.name)

        total_p = session.scalar(select(func.count(Product.product_id)))
        total_r = session.scalar(select(func.count(Review.review_id)))
        logger.info("Seeding complete in %.2fs: %d products, %d reviews", time.time() - start_time, total_p, total_r)
        return {"products": total_p, "reviews": total_r}

    except Exception as e:
        session.rollback()
        logger.error("Seeding failed: %s", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
