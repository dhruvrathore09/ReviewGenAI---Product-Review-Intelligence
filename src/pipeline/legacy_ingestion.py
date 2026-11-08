"""Legacy Level 1 data ingestion pipeline orchestrator for Amazon Reviews 2023 dataset."""

import logging
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from src.config import (
    DATA_DIR,
    DEFAULT_TARGET_REVIEWS,
    LOCAL_META_CACHE,
    PRODUCTS_CSV_PATH,
    REVIEWS_CSV_PATH,
)
from src.data_cleaner import clean_products, clean_reviews
from src.data_loader import (
    ensure_metadata_shard,
    load_product_catalog,
    stream_customer_reviews,
)

logger = logging.getLogger(__name__)


def run_data_pipeline(
    target_reviews: int = DEFAULT_TARGET_REVIEWS,
    output_dir: Path = DATA_DIR,
    save_csv: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """Runs the Level 1 data ingestion, cleaning, and export pipeline."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("STARTING AMAZON REVIEWS 2023 REPRODUCIBLE DATA PIPELINE")
    logger.info(f"Target Review Sample: {target_reviews:,}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info("=" * 60)

    # Step 1: Ensure metadata catalog shard is available
    meta_shard_path = ensure_metadata_shard(local_path=output_dir / "meta_shard0.parquet")
    meta_df, valid_asins = load_product_catalog(meta_shard_path)

    # Step 2: Stream reviews incrementally matching catalog products
    raw_reviews = stream_customer_reviews(
        valid_asins=valid_asins,
        target_count=target_reviews,
    )

    # Step 3: Clean and deduplicate reviews
    reviews_df = clean_reviews(raw_reviews)

    # Step 4: Extract and clean matching product metadata
    selected_product_ids = set(reviews_df["product_id"].unique())
    products_df = clean_products(meta_df, selected_product_ids)

    # Step 5: Save processed CSV files
    reviews_path = output_dir / "reviews.csv"
    products_path = output_dir / "products.csv"

    if save_csv:
        logger.info(f"Writing cleaned reviews to {reviews_path}...")
        reviews_df.to_csv(reviews_path, index=False, encoding="utf-8")
        logger.info(f"Writing cleaned products to {products_path}...")
        products_df.to_csv(products_path, index=False, encoding="utf-8")

    # Step 6: Compute summary metrics
    summary = {
        "total_reviews": len(reviews_df),
        "total_products": len(products_df),
        "avg_star_rating": round(float(reviews_df["star_rating"].mean()), 2),
        "verified_purchase_pct": round(float((reviews_df["verified_purchase"].sum() / len(reviews_df)) * 100), 2),
        "total_helpful_votes": int(reviews_df["helpful_votes"].sum()),
        "reviews_with_title_pct": round(float((reviews_df["review_title"].str.len() > 0).mean() * 100), 2),
        "products_with_image_pct": round(float((products_df["image_url"].str.len() > 0).mean() * 100), 2),
        "products_with_brand_pct": round(float((products_df["brand"] != "Unknown").mean() * 100), 2),
        "earliest_review_date": str(reviews_df["review_date"].min()),
        "latest_review_date": str(reviews_df["review_date"].max()),
        "reviews_file_size_kb": round(reviews_path.stat().st_size / 1024, 2) if reviews_path.exists() else 0,
        "products_file_size_kb": round(products_path.stat().st_size / 1024, 2) if products_path.exists() else 0,
    }

    logger.info("=" * 60)
    logger.info("DATA PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"Collected Reviews: {summary['total_reviews']:,}")
    logger.info(f"Matched Products: {summary['total_products']:,}")
    logger.info(f"Average Star Rating: {summary['avg_star_rating']} / 5.0")
    logger.info(f"Verified Purchase Rate: {summary['verified_purchase_pct']}%")
    logger.info(f"Date Range: {summary['earliest_review_date']} to {summary['latest_review_date']}")
    logger.info(f"Files Generated: {reviews_path.name} ({summary['reviews_file_size_kb']:.1f} KB), {products_path.name} ({summary['products_file_size_kb']:.1f} KB)")
    logger.info("=" * 60)

    return reviews_df, products_df, summary

