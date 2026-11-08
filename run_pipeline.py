#!/usr/bin/env python3
"""CLI Entrypoint for running the Amazon Reviews 2023 data pipeline."""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import DATA_DIR, DEFAULT_TARGET_REVIEWS, MAX_SAMPLE_SIZE, MIN_SAMPLE_SIZE
from src.pipeline import run_data_pipeline


def setup_logging():
    """Sets up formatted stdout logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    parser = argparse.ArgumentParser(
        description="Fetch, clean, and match a reproducible sample of Amazon Reviews 2023 dataset."
    )
    parser.add_argument(
        "--target-reviews",
        type=int,
        default=DEFAULT_TARGET_REVIEWS,
        help=f"Target number of reviews to collect (default: {DEFAULT_TARGET_REVIEWS}, recommended: {MIN_SAMPLE_SIZE}-{MAX_SAMPLE_SIZE})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DATA_DIR),
        help=f"Directory to save reviews.csv and products.csv (default: {DATA_DIR})",
    )

    args = parser.parse_args()
    setup_logging()

    if args.target_reviews < MIN_SAMPLE_SIZE or args.target_reviews > MAX_SAMPLE_SIZE:
        logging.warning(
            f"Target sample {args.target_reviews:,} is outside the recommended range "
            f"({MIN_SAMPLE_SIZE:,} - {MAX_SAMPLE_SIZE:,}). Proceeding as requested."
        )

    reviews_df, products_df, summary = run_data_pipeline(
        target_reviews=args.target_reviews,
        output_dir=Path(args.output_dir),
    )

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    for key, val in summary.items():
        print(f"  {key:<25}: {val}")
    print("=" * 60)


if __name__ == "__main__":
    main()

