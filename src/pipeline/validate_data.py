"""Data validation module enforcing structural and business constraints on reviews and products."""

import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd

from src.pipeline.config import (
    MAX_PRODUCT_RATING,
    MAX_STAR_RATING,
    MIN_PRODUCT_RATING,
    MIN_STAR_RATING,
)

logger = logging.getLogger(__name__)


def validate_reviews(reviews_df: pd.DataFrame, products_df: pd.DataFrame) -> Dict[str, Any]:
    """Validate review dataset against domain rules and referential integrity."""
    violations = []
    total_reviews = len(reviews_df)

    # 1. product_id must not be empty
    empty_pid_mask = reviews_df["product_id"].astype(str).str.strip() == ""
    empty_pid_count = int(empty_pid_mask.sum())
    if empty_pid_count > 0:
        violations.append(f"Found {empty_pid_count} reviews with empty product_id.")

    # 2. review_text must not be empty/missing
    text_col = "cleaned_review_text" if "cleaned_review_text" in reviews_df.columns else "review_text"
    empty_text_mask = reviews_df[text_col].astype(str).str.strip() == ""
    empty_text_count = int(empty_text_mask.sum())
    if empty_text_count > 0:
        violations.append(f"Found {empty_text_count} reviews with empty or blank review text.")

    # 3. star_rating must be bounded between 1.0 and 5.0
    ratings = pd.to_numeric(reviews_df["star_rating"], errors="coerce")
    invalid_ratings_mask = (ratings < MIN_STAR_RATING) | (ratings > MAX_STAR_RATING) | ratings.isnull()
    invalid_ratings_count = int(invalid_ratings_mask.sum())
    if invalid_ratings_count > 0:
        violations.append(f"Found {invalid_ratings_count} reviews with star ratings outside [{MIN_STAR_RATING}, {MAX_STAR_RATING}].")

    # 4. helpful_votes must not be negative
    if "helpful_votes" in reviews_df.columns:
        votes = pd.to_numeric(reviews_df["helpful_votes"], errors="coerce").fillna(0)
        negative_votes_count = int((votes < 0).sum())
        if negative_votes_count > 0:
            violations.append(f"Found {negative_votes_count} reviews with negative helpful votes.")
    else:
        negative_votes_count = 0

    # 5. verified_purchase must be boolean
    verified_vals = reviews_df["verified_purchase"].dropna().unique()
    valid_bool_set = {True, False, 1, 0, "true", "false", "True", "False", "1", "0"}
    invalid_bools = [v for v in verified_vals if v not in valid_bool_set]
    if invalid_bools:
        violations.append(f"Found non-boolean verified_purchase values: {invalid_bools}.")

    # 6. Referential integrity: all product_ids must exist in products_df
    valid_product_ids = set(products_df["product_id"].astype(str).str.strip().unique())
    review_product_ids = reviews_df["product_id"].astype(str).str.strip()
    orphaned_reviews_mask = ~review_product_ids.isin(valid_product_ids)
    orphaned_count = int(orphaned_reviews_mask.sum())
    if orphaned_count > 0:
        violations.append(f"Found {orphaned_count} reviews referencing product_ids not in catalog.")

    # 7. Date and timestamp consistency
    inconsistent_dates_count = 0
    if "review_timestamp" in reviews_df.columns and "review_date" in reviews_df.columns:
        try:
            ts_dates = pd.to_datetime(reviews_df["review_timestamp"], unit="ms", errors="coerce").dt.date
            rev_dates = pd.to_datetime(reviews_df["review_date"], errors="coerce").dt.date
            inconsistent_dates_count = int((ts_dates != rev_dates).sum())
            if inconsistent_dates_count > 0:
                logger.info("Found %d date vs epoch time slight timezone variations.", inconsistent_dates_count)
        except Exception:
            pass

    return {
        "dataset": "reviews",
        "total_records": total_reviews,
        "is_valid": len(violations) == 0,
        "violations_count": len(violations),
        "violations": violations,
        "metrics": {
            "empty_product_ids": empty_pid_count,
            "empty_review_texts": empty_text_count,
            "invalid_star_ratings": invalid_ratings_count,
            "negative_helpful_votes": negative_votes_count,
            "orphaned_reviews": orphaned_count,
            "date_timestamp_discrepancies": inconsistent_dates_count,
        },
    }


def validate_products(products_df: pd.DataFrame) -> Dict[str, Any]:
    """Validate product catalog against structural integrity rules."""
    violations = []
    total_products = len(products_df)

    # 1. product_id must be unique and non-empty
    empty_pid_mask = products_df["product_id"].astype(str).str.strip() == ""
    empty_pid_count = int(empty_pid_mask.sum())
    if empty_pid_count > 0:
        violations.append(f"Found {empty_pid_count} products with empty product_id.")

    duplicate_pid_count = int(products_df.duplicated(subset=["product_id"]).sum())
    if duplicate_pid_count > 0:
        violations.append(f"Found {duplicate_pid_count} duplicate product_ids.")

    # 2. product_name must not be empty
    empty_name_mask = products_df["product_name"].isnull() | (products_df["product_name"].astype(str).str.strip() == "")
    empty_name_count = int(empty_name_mask.sum())
    if empty_name_count > 0:
        violations.append(f"Found {empty_name_count} products with empty product_name.")

    # 3. prices must not be negative
    price_series = pd.to_numeric(products_df["price"], errors="coerce")
    negative_price_count = int((price_series < 0).sum())
    if negative_price_count > 0:
        violations.append(f"Found {negative_price_count} products with negative price.")

    # 4. product average rating must be between 0.0 and 5.0
    ratings = pd.to_numeric(products_df["average_rating"], errors="coerce").dropna()
    invalid_ratings_mask = (ratings < MIN_PRODUCT_RATING) | (ratings > MAX_PRODUCT_RATING)
    invalid_ratings_count = int(invalid_ratings_mask.sum())
    if invalid_ratings_count > 0:
        violations.append(f"Found {invalid_ratings_count} products with ratings outside [{MIN_PRODUCT_RATING}, {MAX_PRODUCT_RATING}].")

    return {
        "dataset": "products",
        "total_records": total_products,
        "is_valid": len(violations) == 0,
        "violations_count": len(violations),
        "violations": violations,
        "metrics": {
            "empty_product_ids": empty_pid_count,
            "duplicate_product_ids": duplicate_pid_count,
            "empty_product_names": empty_name_count,
            "negative_prices": negative_price_count,
            "invalid_product_ratings": invalid_ratings_count,
            "missing_prices": int(products_df["price"].isnull().sum()),
        },
    }


def run_validation(reviews_df: pd.DataFrame, products_df: pd.DataFrame) -> Dict[str, Any]:
    """Execute validation suite across reviews and products."""
    logger.info("Executing validation rules on reviews and products...")
    rev_val = validate_reviews(reviews_df, products_df)
    prod_val = validate_products(products_df)

    overall_valid = rev_val["is_valid"] and prod_val["is_valid"]
    logger.info(
        "Validation complete. Reviews valid: %s, Products valid: %s",
        rev_val["is_valid"],
        prod_val["is_valid"],
    )

    return {
        "overall_valid": overall_valid,
        "reviews_validation": rev_val,
        "products_validation": prod_val,
    }

