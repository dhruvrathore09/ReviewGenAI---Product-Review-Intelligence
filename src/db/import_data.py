"""Transactional ETL pipeline to import CSV data into PostgreSQL database."""

import csv
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from sqlalchemy import insert, select, func, text
from sqlalchemy.orm import Session

from src.db.connection import engine, SessionLocal
from src.db.models import Base, Product, Review
from src.config import PRODUCTS_CSV_PATH, REVIEWS_CSV_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def parse_products_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Read products.csv and cast columns into typed dictionaries."""
    if not file_path.exists():
        raise FileNotFoundError(f"Products CSV file not found: {file_path}")

    products = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_price = row.get("price", "").strip()
            price_val = float(raw_price) if raw_price and raw_price.lower() != "nan" else None

            raw_avg = row.get("average_rating", "").strip()
            avg_rating = float(raw_avg) if raw_avg and raw_avg.lower() != "nan" else None

            raw_num = row.get("rating_number", "").strip()
            rating_num = int(raw_num) if raw_num and raw_num.isdigit() else 0

            products.append(
                {
                    "product_id": row["product_id"].strip(),
                    "product_name": row["product_name"].strip(),
                    "main_category": row.get("main_category", "").strip() or None,
                    "categories_hierarchy": row.get("categories_hierarchy", "").strip() or None,
                    "price": price_val,
                    "brand": row.get("brand", "").strip() or None,
                    "image_url": row.get("image_url", "").strip() or None,
                    "average_rating": avg_rating,
                    "rating_number": rating_num,
                }
            )
    logger.info("Parsed %d product records from %s", len(products), file_path)
    return products


def parse_reviews_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Read reviews.csv and cast columns into typed dictionaries."""
    if not file_path.exists():
        raise FileNotFoundError(f"Reviews CSV file not found: {file_path}")

    reviews = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_helpful = row.get("helpful_votes", "").strip()
            helpful = int(raw_helpful) if raw_helpful and raw_helpful.isdigit() else 0

            verified = str(row.get("verified_purchase", "")).strip().lower() in ("true", "1")

            date_str = row.get("review_date", "").strip()
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            reviews.append(
                {
                    "product_id": row["product_id"].strip(),
                    "user_id": row.get("user_id", "").strip() or None,
                    "review_title": row.get("review_title", "").strip() or None,
                    "review_text": row.get("review_text", ""),
                    "star_rating": float(row["star_rating"]),
                    "review_timestamp": int(row["review_timestamp"]),
                    "review_date": dt,
                    "helpful_votes": helpful,
                    "verified_purchase": verified,
                }
            )
    logger.info("Parsed %d review records from %s", len(reviews), file_path)
    return reviews


def import_dataset(
    products_path: Path = PRODUCTS_CSV_PATH,
    reviews_path: Path = REVIEWS_CSV_PATH,
    batch_size: int = 1000,
    reset_tables: bool = True,
    simulate_failure: bool = False,
) -> Dict[str, int]:
    """
    Import products and reviews inside an atomic transaction.
    
    If any error occurs or simulate_failure is True, all changes are rolled back.
    """
    if reset_tables:
        logger.info("Resetting tables before transactional import...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    products_data = parse_products_csv(products_path)
    reviews_data = parse_reviews_csv(reviews_path)

    start_time = time.time()
    session: Session = SessionLocal()

    try:
        # Begin explicit atomic transaction
        logger.info("Beginning database transaction...")
        session.begin()

        # 1. Insert products in batches
        logger.info("Importing %d products in batches of %d...", len(products_data), batch_size)
        for i in range(0, len(products_data), batch_size):
            batch = products_data[i : i + batch_size]
            session.execute(insert(Product), batch)
            logger.info("Inserted products batch %d - %d", i + 1, min(i + batch_size, len(products_data)))

        # 2. Insert reviews in batches
        logger.info("Importing %d reviews in batches of %d...", len(reviews_data), batch_size)
        for i in range(0, len(reviews_data), batch_size):
            batch = reviews_data[i : i + batch_size]
            session.execute(insert(Review), batch)
            logger.info("Inserted reviews batch %d - %d", i + 1, min(i + batch_size, len(reviews_data)))

        # 3. Simulate failure test if requested
        if simulate_failure:
            raise RuntimeError("SIMULATED ERROR: Verifying transaction rollback behavior!")

        # 4. Commit transaction
        session.commit()
        logger.info("Transaction committed successfully in %.2f seconds!", time.time() - start_time)

    except Exception as exc:
        session.rollback()
        logger.error("Transaction rolled back due to error: %s", exc)
        raise
    finally:
        session.close()

    # Query back row counts for verification
    with SessionLocal() as verify_session:
        prod_count = verify_session.scalar(select(func.count(Product.product_id)))
        rev_count = verify_session.scalar(select(func.count(Review.review_id)))

    logger.info("Post-import database counts: %d products, %d reviews", prod_count, rev_count)
    return {"products": prod_count, "reviews": rev_count}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transactional importer for products and reviews.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for bulk insertion")
    parser.add_argument("--test-rollback", action="store_true", help="Simulate a failure to verify rollback safety")
    args = parser.parse_args()

    if args.test_rollback:
        logger.info("Running Transaction Rollback Verification Test...")
        try:
            import_dataset(batch_size=args.batch_size, simulate_failure=True)
        except RuntimeError:
            # Check row counts after rollback
            with SessionLocal() as s:
                p_c = s.scalar(select(func.count(Product.product_id)))
                r_c = s.scalar(select(func.count(Review.review_id)))
            logger.info("VERIFIED: Database row counts after rollback: %d products, %d reviews (0 expected).", p_c, r_c)
            assert p_c == 0 and r_c == 0, "Rollback failed! Tables are not empty."
            logger.info("Transaction rollback safety successfully verified!")
    else:
        import_dataset(batch_size=args.batch_size)

