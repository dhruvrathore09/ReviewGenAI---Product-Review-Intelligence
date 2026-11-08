"""Endpoints for querying product customer reviews with filters and pagination."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.api.schemas.review import ReviewListResponse
from src.api.services.review_service import ReviewService

router = APIRouter(prefix="/products", tags=["Reviews"])


@router.get(
    "/{product_id}/reviews",
    response_model=ReviewListResponse,
    summary="Get Product Reviews",
    description="Retrieve paginated customer reviews for a given product with filtering by rating and verified status.",
)
def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Reviews per page (max 100)"),
    star_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Filter by exact star rating (e.g. 5.0, 1.0)"),
    verified_only: Optional[bool] = Query(None, description="When true, returns only verified purchase reviews"),
    sort_by: str = Query(
        "date",
        pattern="^(date|rating|helpful|helpful_votes)$",
        description="Sort field: date, rating, or helpful",
    ),
    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Sort direction: asc or desc",
    ),
    db: Session = Depends(get_db),
):
    """Fetch paginated customer reviews for the specified product."""
    result = ReviewService.get_product_reviews(
        db=db,
        product_id=product_id.strip(),
        page=page,
        page_size=page_size,
        star_rating=star_rating,
        verified_only=verified_only,
        sort_by=sort_by,
        order=order,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' was not found in the catalog.",
        )

    return result

