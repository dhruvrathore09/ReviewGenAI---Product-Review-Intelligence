"""Endpoints for product discovery, listing, searching, details, and statistics."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.api.schemas.product import ProductListResponse, ProductDetail, ProductStatistics
from src.api.schemas.report import ProductIntelligenceReport
from src.api.services.product_service import ProductService
from src.api.services.product_report_service import ProductReportService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List Electronic Products",
    description="Retrieve a paginated, filtered, and sorted catalog of electronic products.",
)
def list_products(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    brand: Optional[str] = Query(None, description="Filter by exact brand name (case-insensitive)"),
    category: Optional[str] = Query(None, description="Filter by category or section (case-insensitive)"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum average star rating"),
    max_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Maximum average star rating"),
    sort_by: str = Query(
        "rating_number",
        pattern="^(rating|rating_number|price|name|review_count)$",
        description="Field to sort by: rating, rating_number, price, name, review_count",
    ),
    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Sort direction: asc or desc",
    ),
    q: Optional[str] = Query(None, description="Optional search keyword(s) matching title or brand"),
    db: Session = Depends(get_db),
):
    """List products with optional filtering and pagination."""
    if min_rating is not None and max_rating is not None and min_rating > max_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_rating cannot be greater than max_rating",
        )

    return ProductService.list_products(
        db=db,
        page=page,
        page_size=page_size,
        brand=brand,
        category=category,
        min_rating=min_rating,
        max_rating=max_rating,
        sort_by=sort_by,
        order=order,
        q=q,
    )


@router.get(
    "/search",
    response_model=ProductListResponse,
    summary="Search Products",
    description="Search products by title, name, or manufacturer brand with optional category and brand scoping.",
)
def search_products(
    q: str = Query(..., min_length=1, description="Search keyword(s) matching title or brand"),
    category: Optional[str] = Query(None, description="Optional category or section filter"),
    brand: Optional[str] = Query(None, description="Optional brand filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page"),
    db: Session = Depends(get_db),
):
    """Search products using keyword filtering across name and brand."""
    return ProductService.search_products(
        db=db,
        query=q,
        category=category,
        brand=brand,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{product_id}",
    response_model=ProductDetail,
    summary="Get Product Details",
    description="Retrieve comprehensive details and stored review counts for a specific product ASIN.",
)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Fetch single product detail by ASIN identifier."""
    product = ProductService.get_product_by_id(db=db, product_id=product_id.strip())
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' was not found in the catalog.",
        )
    return product


@router.get(
    "/{product_id}/statistics",
    response_model=ProductStatistics,
    summary="Get Product Rating Statistics",
    description="Compute full rating distributions, average review ratings, and verified ratios from stored reviews.",
)
def get_product_statistics(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Fetch computed rating statistics and distribution for a product."""
    stats = ProductService.get_product_statistics(db=db, product_id=product_id.strip())
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' was not found in the catalog.",
        )
    return stats


@router.get(
    "/{product_id}/report",
    response_model=ProductIntelligenceReport,
    summary="Get Product Intelligence & Review Report",
    description="Synthesize an executive intelligence report evaluating overall rating, durability, lifespan, performance, and verified user pros/cons.",
)
def get_product_intelligence_report(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Fetch synthesized product intelligence and review report for a product."""
    report = ProductReportService.generate_report(db=db, product_id=product_id.strip())
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' was not found in the catalog.",
        )
    return report


