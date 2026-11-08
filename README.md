# Product Review Intelligence Platform - Data Ingestion Pipeline

This module implements a streaming data ingestion and cleaning pipeline for the **Amazon Reviews 2023** dataset (`McAuley-Lab/Amazon-Reviews-2023`), specifically targeting the **Electronics** category.

---

## 1. Dataset Overview

* **Source**: [McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) (UC San Diego).
* **Category**: `Electronics`
* **Raw Size**: Over 21 GB (tens of millions of reviews).
* **Ingestion Strategy**: Incremental HTTP chunked streaming (`requests.iter_lines`).
  * Downloads **zero unneeded reviews** to disk.
  * Streams reviews directly into memory, cleans them, joins matching metadata, and writes production CSVs.

---

## 2. Directory Structure

```text
Product Review Intelligence Platform/
├── data/
│   ├── reviews.csv              # Cleaned customer reviews (7,991 records)
│   ├── products.csv             # Matching product metadata (5,027 records)
│   └── meta_shard0.parquet      # Cached regional metadata shard (209 MB)
├── src/
│   ├── __init__.py
│   ├── config.py                # Pipeline configurations & schemas
│   ├── data_loader.py           # Streaming reader & parquet metadata loader
│   ├── data_cleaner.py          # Data cleansing, deduplication & normalization
│   └── pipeline.py              # End-to-end pipeline orchestrator
├── run_pipeline.py              # CLI entry point to run pipeline
├── inspect_dataset.py           # Data quality inspection & verification script
├── requirements.txt             # Locked Python dependencies
└── README.md                    # Project documentation
```

---

## 3. Data Schema & Fields

### `data/reviews.csv` (7,991 rows)

| Column | Type | Description |
| :--- | :--- | :--- |
| `product_id` | `string` | Amazon `parent_asin` linking review to product |
| `review_title` | `string` | Headline summary of the review |
| `review_text` | `string` | Complete original text of the customer review |
| `star_rating` | `float` | Star rating (1.0 to 5.0) |
| `review_timestamp` | `int64` | Raw millisecond epoch timestamp |
| `review_date` | `string` | Human-readable UTC date (`YYYY-MM-DD HH:MM:SS`) |
| `helpful_votes` | `int64` | Number of helpful votes received from other users |
| `verified_purchase`| `bool` | Whether the review is from a verified purchase |
| `user_id` | `string` | Anonymized customer identifier |

### `data/products.csv` (5,027 rows)

| Column | Type | Description |
| :--- | :--- | :--- |
| `product_id` | `string` | Primary Product Identifier (`parent_asin`) |
| `product_name` | `string` | Full title/name of the item |
| `main_category` | `string` | High-level Amazon category (e.g. `Computers`, `All Electronics`) |
| `categories_hierarchy`| `string` | Breadcrumb category path (e.g. `Electronics > Computers > ...`) |
| `price` | `string` | Listing price in USD |
| `brand` | `string` | Store or manufacturer brand name |
| `image_url` | `string` | Primary high-resolution / large product image URL |
| `average_rating` | `float` | Average Amazon star rating for the product |
| `rating_number` | `int64` | Total historical review count for the product |

---

## 4. How to Reproduce the Pipeline

### Setup Environment
```bash
# Activate virtual environment
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux / macOS

# Install dependencies
pip install -r requirements.txt
```

### Run the Pipeline
```bash
# Run with default 8,000 target reviews
python run_pipeline.py

# Run with custom sample size (e.g., 6,000)
python run_pipeline.py --target-reviews 6000
```

### Inspect the Dataset
```bash
python inspect_dataset.py
```

---

## 5. Verification & Referential Integrity

* **Integrity**: 100% of reviews in `reviews.csv` reference a valid product in `products.csv`.
* **Zero Fake Data**: All reviews, ratings, and customer timestamps are real data directly from Amazon customers via the McAuley Lab 2023 collection.

---

## 6. Level 3 — FastAPI Backend

A production-grade, modular FastAPI REST backend connecting to PostgreSQL (`product_review_db`) via SQLAlchemy.

### Backend Folder Structure

```text
src/api/
├── main.py                     # FastAPI application factory & router mounting
├── dependencies.py             # Database session dependency injection (get_db)
│
├── routes/
│   ├── health.py               # GET /api/health
│   ├── products.py             # GET /api/products, search, details, stats
│   ├── reviews.py              # GET /api/products/{id}/reviews
│   └── dashboard.py            # GET /api/dashboard/overview
│
├── schemas/
│   ├── product.py              # Pydantic schemas for products & stats
│   ├── review.py               # Pydantic schemas for customer reviews
│   └── dashboard.py            # Pydantic schemas for platform metrics
│
└── services/
    ├── product_service.py      # Business logic & SQL queries for products
    ├── review_service.py       # Business logic & SQL queries for reviews
    └── dashboard_service.py    # Business logic & SQL queries for platform aggregates
```

### Running the API Server

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run FastAPI with Uvicorn (hot reload enabled)
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Running Automated API Tests

```bash
# Execute pytest suite across all endpoints
pytest -v
```

### Available REST Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check verifying API and PostgreSQL connectivity |
| `GET` | `/api/products` | Paginated product catalog with filtering (brand, category, rating) and sorting |
| `GET` | `/api/products/search` | Search products by title or brand keywords (`?q=...`) |
| `GET` | `/api/products/{product_id}` | Detailed product attributes, price, image, and stored review count |
| `GET` | `/api/products/{product_id}/reviews` | Paginated customer reviews with rating and verified purchase filters |
| `GET` | `/api/products/{product_id}/statistics` | Rating distribution (1-5 stars), average review rating, and verified ratio |
| `GET` | `/api/dashboard/overview` | Platform-wide metrics (total products, reviews, global rating breakdown, top brands) |

---

## 7. Level 4 — Data Processing Pipeline

A modular, production-grade data processing and feature engineering pipeline built with Python, Pandas, and NumPy. It prepares raw customer review data and product metadata for subsequent machine learning (Level 5 Sentiment Analysis) and NLP extraction (Level 6 Aspect-Based Feedback).

### Pipeline Folder Structure

```text
src/pipeline/
├── __init__.py
├── config.py                 # File paths, thresholds, schema definitions
├── load_data.py              # PostgreSQL ingestion with safe CSV fallback
├── profiling.py              # Statistical distributions, null audits, character lengths
├── clean_reviews.py          # Context-preserving cleaner (Unicode NFKC, negations preserved)
├── clean_products.py         # Metadata cleaner, type conversions, price validation
├── validate_data.py          # Strict data validation (bounds, foreign keys, non-null fields)
├── duplicate_detection.py    # Exact duplicates, event key duplicates, content duplicates
├── feature_engineering.py    # Lexical, temporal, and proxy sentiment features
├── save_processed_data.py    # Atomic file writing via temporary files and rename
└── run_pipeline.py           # CLI runner orchestrating the end-to-end pipeline
```

### Running the Data Processing Pipeline

```bash
# Activate virtual environment
.venv\Scripts\activate

# Execute the complete pipeline
python -m src.pipeline.run_pipeline
```

### Pipeline Outputs and Artifacts

* **`processed_data/reviews_processed.csv`** (7,991 records): Cleaned text, normalized titles, lexical lengths (`review_text_length`, `review_word_count`, `title_length`), temporal features (`review_year`, `review_month`, `review_quarter`), and proxy sentiment (`rating_category`).
* **`processed_data/products_processed.csv`** (5,027 records): Cleaned product metadata with validated numerical prices and preserved `NULL` values.
* **`processed_data/data_quality_report.json`**: Detailed audit of validation checks and duplicate detection.
* **`processed_data/processing_summary.json`**: Execution metrics, runtime, record counts, and category distributions.
* **`reports/data_profiling_report.md`**: Statistical profiling report documenting distributions, percentiles, and quality metrics.

### Running Pipeline Unit and Integration Tests

```bash
pytest tests/test_cleaning.py tests/test_validation.py tests/test_duplicates.py tests/test_feature_engineering.py tests/test_profiling.py tests/test_pipeline_reproducibility.py -v
```

---

## 8. Level 5 — Sentiment Analysis using Machine Learning

A modular, production-grade machine learning module (`src/ml/`) evaluating Scikit-learn classification models on processed customer review text using TF-IDF n-gram vectorization with strict featurization ordering.

### ML Package Structure

```text
src/ml/
├── __init__.py
├── config.py                 # Split ratios (70/15/15), TF-IDF params, random seed (42)
├── dataset.py                # Dataset filtering (Exp A binary vs Exp B 3-class) & text concatenation
├── split.py                  # Stratified train/val/test splitting before feature fitting
├── vectorizer.py             # TF-IDF unigram+bigram vectorizer factory & persistence
├── models.py                 # Candidate models: Dummy, MultinomialNB, LogReg (Balanced), Calibrated LinearSVC
├── evaluate.py               # Metrics (Macro/Weighted F1), confusion matrices, slice error analysis
├── persistence.py            # Serializes models, vectorizers, pipelines, metrics, and plots
├── predictor.py              # SentimentPredictor inference interface for single texts and batches
└── run_experiments.py        # Top-level CLI orchestrator running Experiments A & B
```

### Running the ML Experiments

```bash
# Execute end-to-end training and evaluation for Experiments A and B
python -m src.ml.run_experiments
```

### Generated Artifacts

* **`models/experiment_a_binary/`**:
  - `model.joblib`: Best binary model (`Calibrated Linear SVM`, Test Acc: 95.00%, Macro F1: 0.8712)
  - `vectorizer.joblib`: Standalone fitted TF-IDF vectorizer (10,000 terms)
  - `pipeline.joblib`: End-to-end inference pipeline
  - `confusion_matrix.png`: Normalized confusion matrix heatmap
  - `metrics.json`: Complete validation/test benchmarks & slice analysis
* **`models/experiment_b_3class/`**:
  - `model.joblib`: Best 3-class model (`Logistic Regression Balanced`, Test Acc: 86.07%, Macro F1: 0.6679)
  - `vectorizer.joblib`: Standalone fitted TF-IDF vectorizer (10,000 terms)
  - `pipeline.joblib`: End-to-end inference pipeline
  - `confusion_matrix.png`: Normalized confusion matrix heatmap
  - `metrics.json`: Complete validation/test benchmarks & slice analysis
* **`reports/sentiment_model_evaluation_report.md`**: Full evaluation report with benchmark tables and analysis.

### Running ML Unit Tests

```bash
pytest tests/test_ml_dataset.py tests/test_ml_split.py tests/test_ml_vectorizer.py tests/test_ml_evaluate.py tests/test_ml_inference.py -v
```




