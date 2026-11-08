"""Atomic and safe file-writing module for processed data artifacts and reports."""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from src.pipeline.config import (
    DATA_QUALITY_REPORT_JSON,
    PROCESSING_SUMMARY_JSON,
    PRODUCTS_PROCESSED_CSV,
    REVIEWS_PROCESSED_CSV,
)

logger = logging.getLogger(__name__)


def safe_write_dataframe(df: pd.DataFrame, target_path: Path) -> Path:
    """Safely write DataFrame to a temporary file before atomically replacing target."""
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_name(f"{target_path.stem}.tmp{target_path.suffix}")

    try:
        df.to_csv(temp_path, index=False, encoding="utf-8")
        temp_path.replace(target_path)
        logger.info("Saved %d records to %s (%.2f KB)", len(df), target_path, target_path.stat().st_size / 1024)
        return target_path
    finally:
        if temp_path.exists():
            temp_path.unlink()


def safe_write_json(data: Dict[str, Any], target_path: Path) -> Path:
    """Safely serialize JSON to a temporary file before atomically replacing target."""
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_name(f"{target_path.stem}.tmp{target_path.suffix}")

    try:
        with open(temp_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        temp_path.replace(target_path)
        logger.info("Saved JSON report to %s (%.2f KB)", target_path, target_path.stat().st_size / 1024)
        return target_path
    finally:
        if temp_path.exists():
            temp_path.unlink()


def save_processed_pipeline_outputs(
    reviews_df: pd.DataFrame,
    products_df: pd.DataFrame,
    validation_report: Dict[str, Any],
    duplicate_report: Dict[str, Any],
    summary_report: Dict[str, Any],
) -> Dict[str, str]:
    """Save all processed datasets, data quality reports, and summary metrics."""
    logger.info("Saving pipeline outputs to %s...", PRODUCTS_PROCESSED_CSV.parent)

    # 1. Save processed datasets
    rev_file = safe_write_dataframe(reviews_df, REVIEWS_PROCESSED_CSV)
    prod_file = safe_write_dataframe(products_df, PRODUCTS_PROCESSED_CSV)

    # 2. Combine validation and duplicate audit into comprehensive data quality report
    combined_quality_report = {
        "validation": validation_report,
        "duplicate_detection": duplicate_report,
    }
    qual_file = safe_write_json(combined_quality_report, DATA_QUALITY_REPORT_JSON)

    # 3. Save processing execution summary
    sum_file = safe_write_json(summary_report, PROCESSING_SUMMARY_JSON)

    return {
        "reviews_processed_path": str(rev_file),
        "products_processed_path": str(prod_file),
        "data_quality_report_path": str(qual_file),
        "processing_summary_path": str(sum_file),
    }

