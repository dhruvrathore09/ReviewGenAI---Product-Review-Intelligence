"""Configuration settings for the Amazon Reviews 2023 data pipeline."""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Dataset identifiers
DATASET_REPO = "McAuley-Lab/Amazon-Reviews-2023"
CATEGORY = "Electronics"

# Remote source endpoints
REVIEW_STREAM_URL = (
    f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/raw/review_categories/{CATEGORY}.jsonl"
)
META_SHARD_URL = (
    f"https://huggingface.co/datasets/{DATASET_REPO}/resolve/main/raw_meta_{CATEGORY}/full-00000-of-00010.parquet"
)

# Output files
LOCAL_META_CACHE = DATA_DIR / "meta_shard0.parquet"
REVIEWS_CSV_PATH = DATA_DIR / "reviews.csv"
PRODUCTS_CSV_PATH = DATA_DIR / "products.csv"

# Pipeline target parameters
DEFAULT_TARGET_REVIEWS = 8000
MIN_SAMPLE_SIZE = 5000
MAX_SAMPLE_SIZE = 10000

# Required columns for reviews
REVIEW_RAW_FIELDS = [
    "parent_asin",
    "title",
    "text",
    "rating",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
    "user_id",
]

# Output schema for reviews.csv
FINAL_REVIEW_COLUMNS = [
    "product_id",
    "review_title",
    "review_text",
    "star_rating",
    "review_timestamp",
    "review_date",
    "helpful_votes",
    "verified_purchase",
    "user_id",
]

# Required columns for products
META_RAW_FIELDS = [
    "parent_asin",
    "title",
    "main_category",
    "categories",
    "price",
    "store",
    "images",
    "average_rating",
    "rating_number",
]

# Output schema for products.csv
FINAL_PRODUCT_COLUMNS = [
    "product_id",
    "product_name",
    "main_category",
    "categories_hierarchy",
    "price",
    "brand",
    "image_url",
    "average_rating",
    "rating_number",
]

