"""Create PostgreSQL database tables for products and reviews."""

import logging
from sqlalchemy import text
from src.db.connection import engine
from src.db.models import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def init_db(drop_existing: bool = False) -> None:
    """Initialize database tables according to defined ORM models."""
    logger.info("Initializing database tables on engine: %s", engine.url)
    if drop_existing:
        logger.warning("Dropping existing tables (CASCADE)...")
        Base.metadata.drop_all(bind=engine)

    logger.info("Creating tables: products, reviews...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

    # Inspect created tables in database
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
                """
            )
        )
        tables = [row[0] for row in result.fetchall()]
        logger.info("Existing public tables: %s", tables)


if __name__ == "__main__":
    init_db(drop_existing=True)

