"""Configuration settings and file paths for the Level 4 Data Processing Pipeline."""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure output directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Raw inputs
RAW_REVIEWS_CSV = DATA_DIR / "reviews.csv"
RAW_PRODUCTS_CSV = DATA_DIR / "products.csv"

# Processed outputs
REVIEWS_PROCESSED_CSV = PROCESSED_DATA_DIR / "reviews_processed.csv"
PRODUCTS_PROCESSED_CSV = PROCESSED_DATA_DIR / "products_processed.csv"
DATA_QUALITY_REPORT_JSON = PROCESSED_DATA_DIR / "data_quality_report.json"
PROCESSING_SUMMARY_JSON = PROCESSED_DATA_DIR / "processing_summary.json"
PROFILING_REPORT_MD = REPORTS_DIR / "data_profiling_report.md"

# Validation thresholds
MIN_STAR_RATING = 1.0
MAX_STAR_RATING = 5.0
MIN_PRODUCT_RATING = 0.0
MAX_PRODUCT_RATING = 5.0

# Sentiment weak-supervision mapping thresholds
POSITIVE_RATING_THRESHOLD = 4.0
NEUTRAL_RATING_VALUE = 3.0
NEGATIVE_RATING_THRESHOLD = 2.0

