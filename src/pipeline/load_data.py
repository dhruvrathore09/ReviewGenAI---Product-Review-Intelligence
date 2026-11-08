"""Data loading module connecting to PostgreSQL with fallback to raw CSVs."""

import logging
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
from sqlalchemy import select

from src.pipeline.config import RAW_PRODUCTS_CSV, RAW_REVIEWS_CSV

logger = logging.getLogger(__name__)


def load_from_database() -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
    """Attempt to load reviews and products directly from PostgreSQL."""
    try:
        from src.db.connection import engine
        from src.db.models import Product, Review

        logger.info("Connecting to PostgreSQL to load products and reviews...")
        with engine.connect() as conn:
            products_df = pd.read_sql(select(Product), conn)
            reviews_df = pd.read_sql(select(Review), conn)

        if not products_df.empty and not reviews_df.empty:
            logger.info("Loaded %d products and %d reviews from PostgreSQL.", len(products_df), len(reviews_df))
            return reviews_df, products_df
    except Exception as exc:
        logger.warning("Could not load from PostgreSQL (%s). Falling back to CSVs.", exc)
    return None


def load_from_csv(
    reviews_path: Path = RAW_REVIEWS_CSV,
    products_path: Path = RAW_PRODUCTS_CSV,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load reviews and products from CSV files without modifying them."""
    if not reviews_path.exists():
        raise FileNotFoundError(f"Reviews file not found: {reviews_path}")
    if not products_path.exists():
        raise FileNotFoundError(f"Products file not found: {products_path}")

    # Use keep_default_na=False on text columns so literal 'N/A' reviews are preserved
    logger.info("Loading reviews from %s...", reviews_path)
    reviews_df = pd.read_csv(reviews_path, keep_default_na=False)

    logger.info("Loading products from %s...", products_path)
    products_df = pd.read_csv(products_path, keep_default_na=False)

    logger.info("Loaded %d reviews and %d products from CSV.", len(reviews_df), len(products_df))
    return reviews_df, products_df


def load_dataset(prefer_db: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load data preferring PostgreSQL if available, falling back safely to CSV."""
    if prefer_db:
        result = load_from_database()
        if result is not None:
            return result
    return load_from_csv()

