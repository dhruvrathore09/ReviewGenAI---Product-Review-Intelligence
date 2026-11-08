"""Experiment configuration and hyperparameters for review sentiment classification."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_REVIEWS_PATH = PROJECT_ROOT / "processed_data" / "reviews_processed.csv"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Experiment directories
EXP_A_DIR = MODELS_DIR / "experiment_a_binary"
EXP_B_DIR = MODELS_DIR / "experiment_b_3class"

# Feature Specification (Strict Contract Compliance)
FEATURE_COL = "cleaned_review_text"
PROHIBITED_FEATURE_COLS = [
    "review_title",
    "cleaned_review_title",
    "star_rating",
    "rating_category",
    "review_id",
    "product_id",
    "user_id",
    "review_date",
    "review_timestamp",
    "helpful_votes",
    "verified_purchase",
    "review_text_length",
    "review_word_count",
    "title_length",
    "review_year",
    "review_month",
    "review_quarter",
]

# Reproducibility Seeds
# SPLIT_RANDOM_STATE: Establishes a fresh, independent holdout partition for final evaluation
SPLIT_RANDOM_STATE = 2026
MODEL_RANDOM_STATE = 42
RANDOM_STATE = 42

# Dataset Split Ratios (Strict Featurization Ordering: Train / Val / Test)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# TF-IDF Feature Extraction Configuration
TFIDF_MAX_FEATURES = 10000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_SUBLINEAR_TF = True
TFIDF_MIN_DF = 2

# Target Classes
BINARY_CLASSES = ["negative", "positive"]
THREE_CLASSES = ["negative", "neutral", "positive"]

# Weak-Supervision Rating Mapping Thresholds
POSITIVE_RATING_MIN = 4.0
NEUTRAL_RATING_VAL = 3.0
NEGATIVE_RATING_MAX = 2.0
