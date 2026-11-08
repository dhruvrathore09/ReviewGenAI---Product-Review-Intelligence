"""Data cleaning and transformation module for reviews and product metadata."""

import logging
from typing import Any, Dict, List, Set

import numpy as np
import pandas as pd

from src.config import FINAL_PRODUCT_COLUMNS, FINAL_REVIEW_COLUMNS

logger = logging.getLogger(__name__)


def extract_primary_image_url(images_field: Any) -> str:
    """Extracts a single high-quality image URL from nested metadata images dictionary.
    
    Tries 'large' first, then 'hi_res', then 'thumb'.
    """
    if isinstance(images_field, dict):
        for quality in ["large", "hi_res", "thumb"]:
            urls = images_field.get(quality)
            if urls is not None:
                for url in urls:
                    if isinstance(url, str) and url.startswith("http"):
                        return url.strip()
    return ""


def format_category_hierarchy(category_field: Any) -> str:
    """Formats category breadcrumb array into a readable hierarchical string."""
    if isinstance(category_field, (list, np.ndarray)):
        valid_parts = [str(c).strip() for c in category_field if c and str(c).strip()]
        return " > ".join(valid_parts)
    elif isinstance(category_field, str):
        return category_field.strip()
    return ""


def clean_reviews(raw_reviews: List[Dict]) -> pd.DataFrame:
    """Cleans, formats, and deduplicates customer review records.
    
    Args:
        raw_reviews: List of raw review dictionaries streamed from HF.

    Returns:
        Deduplicated, structured pandas DataFrame conforming to FINAL_REVIEW_COLUMNS.
    """
    logger.info(f"Starting review data cleaning on {len(raw_reviews):,} raw records...")
    df = pd.DataFrame(raw_reviews)
    initial_count = len(df)

    # 1. Drop records missing essential fields: parent_asin, text, rating
    df = df.dropna(subset=["parent_asin", "text", "rating"])
    # Discard empty or whitespace-only review text
    df = df[df["text"].astype(str).str.strip().str.len() > 0]
    
    # Ensure rating is within valid 1.0 - 5.0 range
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])
    df = df[(df["rating"] >= 1.0) & (df["rating"] <= 5.0)]
    dropped_missing = initial_count - len(df)
    logger.info(f"Dropped {dropped_missing:,} records missing critical fields (text, rating, asin).")

    # 2. Impute non-critical missing values
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["helpful_vote"] = pd.to_numeric(df.get("helpful_vote", 0), errors="coerce").fillna(0).astype(int)
    df["verified_purchase"] = df.get("verified_purchase", False).fillna(False).astype(bool)
    df["user_id"] = df.get("user_id", "ANONYMOUS").fillna("ANONYMOUS").astype(str)

    # 3. Convert timestamp into readable UTC date string
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["timestamp"] = df["timestamp"].astype(np.int64)
    df["review_date"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce").dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # 4. Remove duplicate reviews
    count_before_dedup = len(df)
    # Deduplicate by parent product and identical text
    df = df.drop_duplicates(subset=["parent_asin", "text"])
    # Also ensure unique user interaction per product and timestamp
    df = df.drop_duplicates(subset=["parent_asin", "user_id", "timestamp"])
    duplicates_removed = count_before_dedup - len(df)
    logger.info(f"Removed {duplicates_removed:,} duplicate reviews.")

    # 5. Rename and align columns to schema
    df = df.rename(
        columns={
            "parent_asin": "product_id",
            "title": "review_title",
            "text": "review_text",
            "rating": "star_rating",
            "timestamp": "review_timestamp",
            "helpful_vote": "helpful_votes",
        }
    )

    clean_df = df[FINAL_REVIEW_COLUMNS].reset_index(drop=True)
    logger.info(f"Review cleaning complete: {len(clean_df):,} final high-quality reviews.")
    return clean_df


def clean_products(
    meta_df: pd.DataFrame,
    selected_product_ids: Set[str],
) -> pd.DataFrame:
    """Extracts, cleans, and structures metadata for products present in the review sample.
    
    Args:
        meta_df: Full catalog DataFrame.
        selected_product_ids: Set of product IDs appearing in cleaned reviews.

    Returns:
        Structured products DataFrame conforming to FINAL_PRODUCT_COLUMNS.
    """
    logger.info(f"Filtering and cleaning metadata for {len(selected_product_ids):,} selected products...")
    
    # Filter to only the products referenced by reviews
    matched_df = meta_df[meta_df["parent_asin"].isin(selected_product_ids)].copy()
    logger.info(f"Found {len(matched_df):,} matching product entries in catalog.")

    # 1. Clean product title / name
    matched_df["product_name"] = matched_df["title"].fillna("Unknown Product").astype(str).str.strip()
    matched_df.loc[matched_df["product_name"] == "", "product_name"] = "Unknown Product"

    # 2. Main category and category hierarchy
    matched_df["main_category"] = matched_df["main_category"].fillna("Electronics").astype(str).str.strip()
    matched_df["categories_hierarchy"] = matched_df["categories"].apply(format_category_hierarchy)

    # 3. Clean price
    matched_df["price"] = matched_df["price"].astype(str).str.strip()
    matched_df["price"] = matched_df["price"].replace({"None": "", "nan": "", "NaN": ""})

    # 4. Clean brand / store
    matched_df["brand"] = matched_df["store"].fillna("Unknown").astype(str).str.strip()
    matched_df.loc[matched_df["brand"].isin(["", "None", "nan"]), "brand"] = "Unknown"

    # 5. Extract primary image URL
    matched_df["image_url"] = matched_df["images"].apply(extract_primary_image_url)

    # 6. Ratings metadata
    matched_df["average_rating"] = pd.to_numeric(matched_df.get("average_rating"), errors="coerce")
    matched_df["rating_number"] = pd.to_numeric(matched_df.get("rating_number"), errors="coerce").fillna(0).astype(int)

    # 7. Deduplicate products by product_id
    matched_df = matched_df.rename(columns={"parent_asin": "product_id"})
    matched_df = matched_df.drop_duplicates(subset=["product_id"])

    clean_products_df = matched_df[FINAL_PRODUCT_COLUMNS].reset_index(drop=True)
    logger.info(f"Product cleaning complete: {len(clean_products_df):,} distinct products formatted.")
    return clean_products_df

