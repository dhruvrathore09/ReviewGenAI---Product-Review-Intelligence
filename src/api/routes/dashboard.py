"""Endpoints for global dashboard metrics and platform aggregates."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.api.schemas.dashboard import (
    DashboardOverviewResponse,
    AnalyticsHubResponse,
    ComparatorProductItem,
    ComparisonItem,
)
from src.api.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Get Platform Dashboard Overview",
    description="Retrieve platform-wide aggregates including total products, reviews, rating distribution, and top brands.",
)
def get_dashboard_overview(
    db: Session = Depends(get_db),
):
    """Fetch global platform intelligence metrics."""
    return DashboardService.get_overview(db=db)


@router.get(
    "/analytics-hub",
    response_model=AnalyticsHubResponse,
    summary="Get Deep Review Analytics Hub Data",
    description="Retrieve category-specific benchmarks, head-to-head product battles, and reliability failure radar.",
)
def get_analytics_hub(
    db: Session = Depends(get_db),
):
    """Fetch structured category benchmarks, comparisons, and failure radars."""
    return DashboardService.get_analytics_hub(db=db)


@router.get(
    "/category-products",
    response_model=List[ComparatorProductItem],
    summary="Get Popular Products for Category Comparator",
    description="Retrieve products within a selected category for head-to-head selection dropdowns.",
)
def get_category_products(
    category: str = Query(..., description="Target category name"),
    limit: int = Query(50, ge=1, le=100, description="Max products to return"),
    db: Session = Depends(get_db),
):
    """Fetch products for interactive comparator selection."""
    return DashboardService.get_category_products(db=db, category=category, limit=limit)


@router.get(
    "/compare",
    response_model=ComparisonItem,
    summary="Compare Two Products Head-to-Head",
    description="Dynamically generate a side-by-side comparison report and executive winner verdict between two products.",
)
def compare_two_products(
    product_a: str = Query(..., description="Product A ASIN ID"),
    product_b: str = Query(..., description="Product B ASIN ID"),
    db: Session = Depends(get_db),
):
    """Generate dynamic head-to-head comparison between any two user-selected products."""
    comparison = DashboardService.compare_products(db=db, product_a_id=product_a, product_b_id=product_b)
    if not comparison:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to generate comparison between '{product_a}' and '{product_b}'. Ensure both products exist.",
        )
    return comparison



