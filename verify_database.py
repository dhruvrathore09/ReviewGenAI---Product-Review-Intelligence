"""Comprehensive database verification script for PostgreSQL integration."""

import csv
from pathlib import Path
from sqlalchemy import text
from src.db.connection import engine
from src.config import PRODUCTS_CSV_PATH, REVIEWS_CSV_PATH


def count_csv_rows(file_path: Path) -> int:
    """Count non-header data rows in a CSV file."""
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        return sum(1 for _ in reader)


def run_sql_query(conn, query_str: str, description: str):
    """Execute SQL query and print description, SQL, and tabular results."""
    print("=" * 80)
    print(f"VERIFICATION CHECK: {description}")
    print("-" * 80)
    print("SQL Query:\n" + query_str.strip() + "\n")
    result = conn.execute(text(query_str))
    
    if result.returns_rows:
        rows = result.fetchall()
        keys = list(result.keys())
        print(f"Columns: {keys}")
        print(f"Row count returned: {len(rows)}")
        if rows:
            # Print sample or all if <= 10
            for i, row in enumerate(rows[:10]):
                print(f"  [{i+1}] {dict(zip(keys, row))}")
            if len(rows) > 10:
                print(f"  ... ({len(rows) - 10} more rows)")
        else:
            print("  (No rows returned - check passed!)")
    else:
        print("Query executed successfully without returned rows.")
    print("=" * 80 + "\n")
    return result


def main():
    print("\n" + "#" * 80)
    print("RUNNING LEVEL 2 POSTGRESQL DATABASE VERIFICATION SUITE")
    print("#" * 80 + "\n")

    # Count rows in CSV files
    csv_products_count = count_csv_rows(PRODUCTS_CSV_PATH)
    csv_reviews_count = count_csv_rows(REVIEWS_CSV_PATH)
    print(f"Original CSV file row counts:")
    print(f"  - products.csv: {csv_products_count} rows")
    print(f"  - reviews.csv:  {csv_reviews_count} rows\n")

    with engine.connect() as conn:
        # Check 1: Total products imported
        res_prod = conn.execute(text("SELECT COUNT(*) AS total_products FROM products;")).scalar()
        print(f"Check 1: Total products in database: {res_prod} (Matches CSV: {res_prod == csv_products_count})")

        # Check 2: Total reviews imported
        res_rev = conn.execute(text("SELECT COUNT(*) AS total_reviews FROM reviews;")).scalar()
        print(f"Check 2: Total reviews in database: {res_rev} (Matches CSV: {res_rev == csv_reviews_count})\n")

        # Check 3: Duplicate product IDs in products table
        run_sql_query(
            conn,
            """
            SELECT product_id, COUNT(*) AS occurrences
            FROM products
            GROUP BY product_id
            HAVING COUNT(*) > 1;
            """,
            "Duplicate Product IDs in 'products' table"
        )

        # Check 4: Duplicate reviews in reviews table
        run_sql_query(
            conn,
            """
            SELECT product_id, user_id, review_timestamp, COUNT(*) AS occurrences
            FROM reviews
            GROUP BY product_id, user_id, review_timestamp
            HAVING COUNT(*) > 1;
            """,
            "Duplicate Reviews in 'reviews' table (by product_id, user_id, timestamp)"
        )

        # Check 5: Orphaned reviews with missing or invalid product references
        run_sql_query(
            conn,
            """
            SELECT r.review_id, r.product_id, r.review_title
            FROM reviews r
            LEFT JOIN products p ON r.product_id = p.product_id
            WHERE p.product_id IS NULL;
            """,
            "Reviews with missing or invalid product references (Foreign Key Integrity)"
        )

        # Check 6: Average review rating calculation
        run_sql_query(
            conn,
            """
            SELECT 
                COUNT(*) AS total_reviews,
                ROUND(AVG(star_rating), 4) AS average_review_rating,
                MIN(star_rating) AS min_rating,
                MAX(star_rating) AS max_rating
            FROM reviews;
            """,
            "Average Review Rating across Individual Customer Reviews"
        )

        # Check 6b: Distribution of star ratings
        run_sql_query(
            conn,
            """
            SELECT 
                star_rating,
                COUNT(*) AS count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) AS percentage
            FROM reviews
            GROUP BY star_rating
            ORDER BY star_rating DESC;
            """,
            "Star Rating Frequency Distribution"
        )

        # Check 7: JOIN query showing product names alongside their reviews
        run_sql_query(
            conn,
            """
            SELECT 
                p.product_id,
                SUBSTRING(p.product_name, 1, 45) AS product_name,
                p.brand,
                r.review_id,
                r.star_rating,
                r.verified_purchase,
                r.review_date,
                SUBSTRING(r.review_text, 1, 55) AS review_snippet
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            ORDER BY r.review_id ASC
            LIMIT 10;
            """,
            "JOIN Query: Product Details alongside Review Data"
        )

        # Check 8: Indexes verification
        run_sql_query(
            conn,
            """
            SELECT 
                tablename, 
                indexname, 
                indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            ORDER BY tablename, indexname;
            """,
            "Public Table Indexes in PostgreSQL"
        )


if __name__ == "__main__":
    main()

