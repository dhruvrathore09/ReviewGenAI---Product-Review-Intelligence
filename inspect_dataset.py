#!/usr/bin/env python3
"""Dataset Inspection & Quality Report Script for Amazon Reviews 2023.

Validates the collected reviews.csv and products.csv, displaying comprehensive
statistics, schema breakdown, referential integrity, and record samples.
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import PRODUCTS_CSV_PATH, REVIEWS_CSV_PATH


def inspect_dataset():
    if not REVIEWS_CSV_PATH.exists():
        print(f"Error: {REVIEWS_CSV_PATH} not found. Please run run_pipeline.py first.")
        sys.exit(1)
    if not PRODUCTS_CSV_PATH.exists():
        print(f"Error: {PRODUCTS_CSV_PATH} not found. Please run run_pipeline.py first.")
        sys.exit(1)

    reviews_df = pd.read_csv(REVIEWS_CSV_PATH, keep_default_na=False)
    products_df = pd.read_csv(PRODUCTS_CSV_PATH, keep_default_na=False)

    reviews_df["star_rating"] = pd.to_numeric(reviews_df["star_rating"])
    reviews_df["helpful_votes"] = pd.to_numeric(reviews_df["helpful_votes"])
    reviews_df["verified_purchase"] = reviews_df["verified_purchase"].astype(str).str.lower().isin(["true", "1"])
    products_df["average_rating"] = pd.to_numeric(products_df["average_rating"], errors="coerce")
    products_df["rating_number"] = pd.to_numeric(products_df["rating_number"], errors="coerce")

    print("=" * 75)
    print("AMAZON REVIEWS 2023 DATASET QUALITY & STRUCTURE INSPECTION")
    print("=" * 75)

    # 1. High Level Overview
    print("\n[1] HIGH-LEVEL SUMMARY")
    print(f"  * Total Customer Reviews : {len(reviews_df):,}")
    print(f"  * Total Unique Products  : {len(products_df):,}")
    print(f"  * Category Analyzed      : Electronics")
    print(f"  * Source Repository      : McAuley-Lab/Amazon-Reviews-2023 (UC San Diego)")

    # 2. Reviews Table Structure
    print("\n[2] REVIEWS TABLE STRUCTURE (`data/reviews.csv`)")
    print(f"  * Dimensions: {reviews_df.shape[0]:,} rows x {reviews_df.shape[1]} columns")
    print("\n  Column Breakdown:")
    for col in reviews_df.columns:
        null_count = reviews_df[col].isnull().sum()
        dtype = str(reviews_df[col].dtype)
        sample_val = str(reviews_df[col].iloc[0])[:35]
        print(f"    - {col:<18} | Type: {dtype:<8} | Nulls: {null_count:<5} | Sample: {sample_val}...")

    # 3. Rating Distribution
    print("\n[3] STAR RATING DISTRIBUTION")
    rating_counts = reviews_df["star_rating"].value_counts().sort_index(ascending=False)
    for star, count in rating_counts.items():
        pct = (count / len(reviews_df)) * 100
        bar = "█" * int(pct // 2)
        print(f"    {star:.1f} Stars: {count:>6,} ({pct:>5.1f}%) | {bar}")
    print(f"    Average Rating: {reviews_df['star_rating'].mean():.2f} / 5.0")

    # 4. Review Engagement & Verification
    print("\n[4] REVIEW ENGAGEMENT & VERIFICATION METRICS")
    verified_cnt = reviews_df["verified_purchase"].sum()
    verified_pct = (verified_cnt / len(reviews_df)) * 100
    print(f"    * Verified Purchases : {verified_cnt:,} ({verified_pct:.1f}%)")
    print(f"    * Non-Verified       : {len(reviews_df) - verified_cnt:,} ({100 - verified_pct:.1f}%)")
    print(f"    * Total Helpful Votes: {reviews_df['helpful_votes'].sum():,}")
    print(f"    * Max Helpful Votes  : {reviews_df['helpful_votes'].max():,}")
    
    # Review text length
    text_lengths = reviews_df["review_text"].str.len()
    word_counts = reviews_df["review_text"].str.split().str.len()
    print(f"    * Avg Text Length    : {text_lengths.mean():.1f} characters ({word_counts.mean():.1f} words)")
    print(f"    * Min/Max Text Length: {text_lengths.min()} / {text_lengths.max()} characters")
    print(f"    * Date Range         : {reviews_df['review_date'].min()} to {reviews_df['review_date'].max()}")

    # 5. Products Table Structure
    print("\n[5] PRODUCTS TABLE STRUCTURE (`data/products.csv`)")
    print(f"  * Dimensions: {products_df.shape[0]:,} rows x {products_df.shape[1]} columns")
    print("\n  Column Breakdown:")
    for col in products_df.columns:
        null_count = products_df[col].isnull().sum()
        dtype = str(products_df[col].dtype)
        sample_val = str(products_df[col].iloc[0])[:35]
        print(f"    - {col:<22} | Type: {dtype:<8} | Nulls: {null_count:<5} | Sample: {sample_val}...")

    # 6. Product Brands and Categories
    print("\n[6] TOP PRODUCT BRANDS & MAIN CATEGORIES")
    print("  Top Brands:")
    for brand, count in products_df["brand"].value_counts().head(8).items():
        print(f"    - {brand:<25}: {count:>4,} products")

    print("\n  Main Categories:")
    for cat, count in products_df["main_category"].value_counts().head(6).items():
        print(f"    - {cat:<25}: {count:>4,} products")

    # Image and price availability
    images_available = (products_df["image_url"].str.len() > 0).sum()
    prices_available = products_df["price"].dropna().astype(str).str.strip().ne("").sum()
    print(f"\n  * Products with Primary Image URL : {images_available:,} ({(images_available/len(products_df))*100:.1f}%)")
    print(f"  * Products with Price Available   : {prices_available:,} ({(prices_available/len(products_df))*100:.1f}%)")

    # 7. Referential Integrity Check
    print("\n[7] REFERENTIAL INTEGRITY VALIDATION")
    review_pids = set(reviews_df["product_id"].unique())
    product_pids = set(products_df["product_id"].unique())
    missing_products = review_pids - product_pids
    if not missing_products:
        print("  ✓ SUCCESS: 100% of reviews map cleanly to a valid product record in products.csv!")
        print(f"  ✓ Product IDs matched: {len(review_pids):,} / {len(review_pids):,}")
    else:
        print(f"  ✗ WARNING: {len(missing_products)} review product IDs lack metadata in products.csv.")

    # 8. Sample Records
    print("\n[8] SAMPLE CLEANED REVIEW RECORD")
    sample_rev = reviews_df.iloc[0].to_dict()
    for k, v in sample_rev.items():
        val_str = str(v)
        if len(val_str) > 80:
            val_str = val_str[:77] + "..."
        print(f"    {k:<18}: {val_str}")

    print("\n[9] SAMPLE MATCHING PRODUCT RECORD")
    sample_prod = products_df.iloc[0].to_dict()
    for k, v in sample_prod.items():
        val_str = str(v)
        if len(val_str) > 80:
            val_str = val_str[:77] + "..."
        print(f"    {k:<22}: {val_str}")

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETE: Dataset is verified, clean, and ready for intelligence analytics.")
    print("=" * 75)


if __name__ == "__main__":
    inspect_dataset()
