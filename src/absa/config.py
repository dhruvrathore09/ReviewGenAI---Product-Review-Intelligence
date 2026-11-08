"""Configuration module for Level 6 Aspect-Based Sentiment Analysis (ABSA)."""

from pathlib import Path
from typing import Dict, List

# 1. Authoritative Data and Output Paths
PROCESSED_REVIEWS_PATH: Path = Path("processed_data/reviews_processed.csv")
ABSA_OUTPUT_DIR: Path = Path("processed_data/absa")

ASPECT_MENTIONS_CSV: Path = Path("processed_data/absa/aspect_mentions.csv")
ASPECT_SENTIMENT_RESULTS_CSV: Path = Path("processed_data/absa/aspect_sentiment_results.csv")
ASPECT_SUMMARY_CSV: Path = Path("processed_data/absa/aspect_summary.csv")
MANUAL_AUDIT_CSV: Path = Path("processed_data/absa/manual_audit_100.csv")
REPORT_PATH: Path = Path("reports/absa_evaluation_report.md")

# 2. Record Identification & Traceability Contract
# IMPORTANT: dataset_row_id is the 0-indexed integer position (0 to 7990) of the review
# record within processed_data/reviews_processed.csv. It guarantees deterministic row-level
# traceability without fabricating or inventing a surrogate key, and is explicitly distinct
# from the PostgreSQL database primary key reviews.review_id.
ROW_ID_COL: str = "dataset_row_id"
PRODUCT_ID_COL: str = "product_id"
USER_ID_COL: str = "user_id"
TIMESTAMP_COL: str = "review_timestamp"

# 3. Approved Aspect Categories Definition
ASPECT_BATTERY: str = "battery"
ASPECT_SOUND: str = "sound_quality"
ASPECT_BUILD: str = "build_quality"
ASPECT_DISPLAY: str = "display"
ASPECT_PRICE: str = "price_value"

ASPECT_CATEGORIES: List[str] = [
    ASPECT_BATTERY,
    ASPECT_SOUND,
    ASPECT_BUILD,
    ASPECT_DISPLAY,
    ASPECT_PRICE,
]

ASPECT_DISPLAY_NAMES: Dict[str, str] = {
    ASPECT_BATTERY: "Battery & Charging",
    ASPECT_SOUND: "Sound Quality",
    ASPECT_BUILD: "Build Quality",
    ASPECT_DISPLAY: "Display & Screen",
    ASPECT_PRICE: "Price & Value",
}

# 4. Sentiment Classes
SENTIMENT_POSITIVE: str = "positive"
SENTIMENT_NEUTRAL: str = "neutral"
SENTIMENT_NEGATIVE: str = "negative"
SENTIMENT_UNCERTAIN: str = "uncertain"

SENTIMENT_LABELS: List[str] = [
    SENTIMENT_POSITIVE,
    SENTIMENT_NEUTRAL,
    SENTIMENT_NEGATIVE,
    SENTIMENT_UNCERTAIN,
]

# 5. Mutually Exclusive Confidence Thresholds
CONFIDENCE_HIGH: float = 0.70      # High-confidence classification
CONFIDENCE_MODERATE: float = 0.60  # Moderate-confidence classification
CONFIDENCE_MINIMUM: float = 0.60   # Scores < 0.60 are strictly labeled 'uncertain'

# 6. Syntactic Contrast & Negation Markers
CONTRAST_CONJUNCTIONS: List[str] = [
    "but",
    "however",
    "although",
    "though",
    "yet",
    "except",
    "while",
    "whereas",
    "on the other hand",
    "nevertheless",
    "nonetheless",
]

NEGATION_MARKERS: List[str] = [
    "not",
    "never",
    "no",
    "none",
    "hardly",
    "barely",
    "scarcely",
    "cannot",
    "cant",
    "can't",
    "wont",
    "won't",
    "isnt",
    "isn't",
    "arent",
    "aren't",
    "didnt",
    "didn't",
    "doesnt",
    "doesn't",
    "wasnt",
    "wasn't",
    "werent",
    "weren't",
    "dont",
    "don't",
    "hasnt",
    "hasn't",
    "havent",
    "haven't",
    "hadnt",
    "hadn't",
    "without",
    "lack",
    "lacking",
]

# Cognitive Matrix Verbs (for negative raising / transferred negation)
COGNITIVE_VERBS: List[str] = [
    "think",
    "believe",
    "feel",
    "find",
    "consider",
]

# Modifiers
INTENSIFIERS: List[str] = [
    "very",
    "extremely",
    "really",
    "super",
    "incredibly",
    "highly",
    "absolutely",
    "totally",
    "completely",
    "especially",
    "exceptionally",
]

DIMINISHERS: List[str] = [
    "slightly",
    "somewhat",
    "a bit",
    "a little",
    "barely",
    "mildly",
    "partially",
]

# 7. Extraction Window Settings
TOKEN_WINDOW_RADIUS: int = 6  # Local window around aspect mention
MAX_SNIPPET_LENGTH: int = 160  # Character ceiling for snippet representation

