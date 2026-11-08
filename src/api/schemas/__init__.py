"""Pydantic schemas package for API request validation and response models."""

from src.api.schemas.product import (
    ProductBase,
    ProductListItem,
    ProductDetail,
    ProductListResponse,
    ProductStatistics,
    RatingDistributionItem,
)
from src.api.schemas.review import ReviewItem, ReviewListResponse
from src.api.schemas.dashboard import (
    DashboardOverviewResponse,
    CategoryOverviewItem,
    BrandOverviewItem,
)

__all__ = [
    "ProductBase",
    "ProductListItem",
    "ProductDetail",
    "ProductListResponse",
    "ProductStatistics",
    "RatingDistributionItem",
    "ReviewItem",
    "ReviewListResponse",
    "DashboardOverviewResponse",
    "CategoryOverviewItem",
    "BrandOverviewItem",
]

