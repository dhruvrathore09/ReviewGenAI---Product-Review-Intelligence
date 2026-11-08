"""Tests verifying pipeline reproducibility and raw data immutability."""

import hashlib
from pathlib import Path
import pytest
from src.pipeline.run_pipeline import execute_pipeline
from src.pipeline.config import (
    RAW_PRODUCTS_CSV,
    RAW_REVIEWS_CSV,
    PRODUCTS_PROCESSED_CSV,
    REVIEWS_PROCESSED_CSV,
)


def get_file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_pipeline_execution_and_artifacts():
    """Verify end-to-end execution generates valid, non-empty processed artifacts."""
    # Hash raw files before execution
    hash_reviews_before = get_file_hash(RAW_REVIEWS_CSV)
    hash_products_before = get_file_hash(RAW_PRODUCTS_CSV)

    # Run pipeline
    results = execute_pipeline(prefer_db=False)  # Test with CSV fallback path as well
    assert results["validation"]["overall_valid"] is True
    assert results["summary"]["processed_records"]["reviews_processed_count"] == 7991
    assert results["summary"]["processed_records"]["products_processed_count"] == 5027

    # Assert outputs exist and have non-zero size
    assert PRODUCTS_PROCESSED_CSV.exists()
    assert REVIEWS_PROCESSED_CSV.exists()
    assert PRODUCTS_PROCESSED_CSV.stat().st_size > 0
    assert REVIEWS_PROCESSED_CSV.stat().st_size > 0

    # Assert raw files were NEVER modified (exact hash match)
    hash_reviews_after = get_file_hash(RAW_REVIEWS_CSV)
    hash_products_after = get_file_hash(RAW_PRODUCTS_CSV)

    assert hash_reviews_before == hash_reviews_after, "Original reviews.csv was modified!"
    assert hash_products_before == hash_products_after, "Original products.csv was modified!"

