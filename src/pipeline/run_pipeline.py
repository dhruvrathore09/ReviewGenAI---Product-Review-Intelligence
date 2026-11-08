"""Main entry point orchestrating the Level 4 Data Processing Pipeline."""

import logging
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any

from src.pipeline.load_data import load_dataset
from src.pipeline.profiling import run_profiling
from src.pipeline.clean_reviews import clean_reviews_dataframe
from src.pipeline.clean_products import clean_products_dataframe
from src.pipeline.validate_data import run_validation
from src.pipeline.duplicate_detection import run_duplicate_audit
from src.pipeline.feature_engineering import engineer_review_features
from src.pipeline.save_processed_data import save_processed_pipeline_outputs
from src.pipeline.config import (
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    REVIEWS_PROCESSED_CSV,
    PRODUCTS_PROCESSED_CSV,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def execute_pipeline(prefer_db: bool = True) -> Dict[str, Any]:
    """Execute the complete data processing workflow in sequence."""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("STARTING LEVEL 4 DATA PROCESSING PIPELINE")
    logger.info("=" * 80)

    # 1. Load Data
    logger.info("\n--- STEP 1: LOAD DATA ---")
    reviews_raw, products_raw = load_dataset(prefer_db=prefer_db)
    initial_reviews_count = len(reviews_raw)
    initial_products_count = len(products_raw)

    # 2. Data Profiling
    logger.info("\n--- STEP 2: DATA PROFILING ---")
    profiling_results = run_profiling(reviews_raw, products_raw, save_report=True)

    # 3. Review Cleaning
    logger.info("\n--- STEP 3: REVIEW TEXT CLEANING ---")
    reviews_cleaned = clean_reviews_dataframe(reviews_raw)

    # 4. Product Cleaning
    logger.info("\n--- STEP 4: PRODUCT METADATA CLEANING ---")
    products_cleaned = clean_products_dataframe(products_raw)

    # 5. Data Validation
    logger.info("\n--- STEP 5: DATA VALIDATION ---")
    validation_results = run_validation(reviews_cleaned, products_cleaned)

    # 6. Duplicate Detection
    logger.info("\n--- STEP 6: DUPLICATE DETECTION ---")
    duplicate_results = run_duplicate_audit(reviews_cleaned, products_cleaned)

    # 7. Feature Engineering
    logger.info("\n--- STEP 7: FEATURE ENGINEERING ---")
    reviews_featured = engineer_review_features(reviews_cleaned)

    # 8. Compute Execution Summary
    execution_duration = round(time.time() - start_time, 2)
    summary = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_duration_seconds": execution_duration,
        "input_records": {
            "reviews_count": initial_reviews_count,
            "products_count": initial_products_count,
        },
        "processed_records": {
            "reviews_processed_count": len(reviews_featured),
            "products_processed_count": len(products_cleaned),
            "rejected_reviews": initial_reviews_count - len(reviews_featured),
            "rejected_products": initial_products_count - len(products_cleaned),
        },
        "quality_metrics": {
            "validation_passed": validation_results["overall_valid"],
            "exact_review_duplicates": duplicate_results["reviews_duplicates"]["exact_duplicates"]["count"],
            "event_key_review_duplicates": duplicate_results["reviews_duplicates"]["event_key_duplicates"]["count"],
        },
        "sentiment_category_distribution": reviews_featured["rating_category"].value_counts().to_dict(),
        "lexical_summary": {
            "mean_word_count": round(float(reviews_featured["review_word_count"].mean()), 2),
            "median_word_count": round(float(reviews_featured["review_word_count"].median()), 2),
            "mean_text_length": round(float(reviews_featured["review_text_length"].mean()), 2),
            "verified_purchase_percentage": round(
                float((reviews_featured["is_verified_purchase"].sum() / len(reviews_featured)) * 100), 2
            ),
        },
    }

    # 9. Save Processed Outputs
    logger.info("\n--- STEP 8: SAVE PROCESSED ARTIFACTS ---")
    saved_paths = save_processed_pipeline_outputs(
        reviews_df=reviews_featured,
        products_df=products_cleaned,
        validation_report=validation_results,
        duplicate_report=duplicate_results,
        summary_report=summary,
    )

    logger.info("=" * 80)
    logger.info("LEVEL 4 DATA PROCESSING PIPELINE COMPLETED SUCCESSFULLY (%.2fs)", execution_duration)
    logger.info("Processed Reviews: %d | Processed Products: %d", len(reviews_featured), len(products_cleaned))
    logger.info("Sentiment Proxy Breakdown: %s", summary["sentiment_category_distribution"])
    logger.info("Artifacts saved to: %s", PROCESSED_DATA_DIR)
    logger.info("Reports saved to: %s", REPORTS_DIR)
    logger.info("=" * 80)

    return {
        "summary": summary,
        "validation": validation_results,
        "duplicates": duplicate_results,
        "saved_paths": saved_paths,
    }


if __name__ == "__main__":
    execute_pipeline()

