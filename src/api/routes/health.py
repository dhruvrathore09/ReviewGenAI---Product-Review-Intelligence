"""Health check endpoint to monitor API and database availability."""

from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Service Health Check",
    description="Verifies the operational status of the FastAPI backend and connectivity to PostgreSQL.",
    status_code=status.HTTP_200_OK,
)
def check_health(db: Session = Depends(get_db)):
    """Health check endpoint returning system status and DB ping."""
    try:
        # Ping PostgreSQL
        db.execute(text("SELECT 1;"))
        db_status = "connected"
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "message": "Database service is temporarily unavailable",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }

