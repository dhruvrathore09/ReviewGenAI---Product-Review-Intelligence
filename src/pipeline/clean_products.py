"""Product catalog data cleaning and metadata normalization module."""

import html
import logging
import re
import unicodedata
from typing import Optional, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def clean_text_field(val: Optional[str]) -> Optional[str]:
    """Clean and normalize string metadata fields (name, brand, category)."""
    if val is None or pd.isna(val):
        return None

    s = str(val)
    if s.strip() == "" or s.strip().lower() in ("nan", "none", "null"):
        return None

    # Normalize Unicode and entities
    norm = unicodedata.normalize("NFKC", s)
    norm = html.unescape(norm)
    norm = re.sub(r"\s+", " ", norm).strip()
    return norm if norm else None


def clean_price_field(val: Union[float, int, str, None]) -> Optional[float]:
    """Clean and cast price value to float, ensuring no negative prices and preserving nulls."""
    if val is None or pd.isna(val):
        return None

    s = str(val).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return None

    try:
        price_num = float(s)
        if price_num < 0:
            logger.warning("Negative price encountered ($%.2f). Setting to None.", price_num)
            return None
        return round(price_num, 2)
    except (ValueError, TypeError):
        return None


def clean_products_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate product catalog fields while preserving missing attributes."""
    logger.info("Cleaning products dataset (%d records)...", len(df))
    out_df = df.copy()

    # 1. Clean text attributes
    out_df["product_id"] = out_df["product_id"].astype(str).str.strip()
    out_df["product_name"] = out_df["product_name"].apply(clean_text_field).fillna("Unknown Product")
    out_df["brand"] = out_df["brand"].apply(clean_text_field).fillna("Unknown")
    out_df["main_category"] = out_df["main_category"].apply(clean_text_field)
    if "categories_hierarchy" in out_df.columns:
        out_df["categories_hierarchy"] = out_df["categories_hierarchy"].apply(clean_text_field)

    # 2. Clean numeric attributes
    out_df["price"] = out_df["price"].apply(clean_price_field)

    out_df["average_rating"] = pd.to_numeric(out_df["average_rating"], errors="coerce")
    # Clamp valid bounds [0.0, 5.0]
    out_df["average_rating"] = out_df["average_rating"].clip(lower=0.0, upper=5.0)

    out_df["rating_number"] = pd.to_numeric(out_df["rating_number"], errors="coerce").fillna(0).astype(int)
    out_df["rating_number"] = out_df["rating_number"].clip(lower=0)

    logger.info("Product cleaning complete.")
    return out_df

