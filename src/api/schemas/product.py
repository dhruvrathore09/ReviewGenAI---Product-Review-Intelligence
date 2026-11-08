"""Pydantic schemas for product-related endpoints."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RatingDistributionItem(BaseModel):
    """Distribution of ratings for a specific star rating."""

    star_rating: float = Field(..., description="Star rating value (e.g. 1.0 to 5.0)")
    count: int = Field(..., description="Total review count for this star rating")
    percentage: float = Field(..., description="Percentage of total reviews")

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    """Core product attributes."""

    product_id: str = Field(..., description="Unique Amazon ASIN")
    product_name: str = Field(..., description="Product title / name")
    brand: Optional[str] = Field(None, description="Manufacturer or brand")
    main_category: Optional[str] = Field(None, description="Primary product category")
    price: Optional[float] = Field(None, description="Listing price in USD")
    image_url: Optional[str] = Field(None, description="Primary product image URL")
    average_rating: Optional[float] = Field(None, description="Catalog average rating")
    rating_number: Optional[int] = Field(0, description="Total historical catalog ratings count")
    honest_rating: Optional[float] = Field(None, description="Honest reality-checked rating")
    flaw_tag: Optional[str] = Field(None, description="Reported failure warning tag")

    model_config = ConfigDict(from_attributes=True)


class ProductListItem(ProductBase):
    """Summary item displayed in product catalogs and search results."""

    db_review_count: int = Field(0, description="Number of customer reviews stored in our platform")


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    total: int = Field(..., description="Total number of matching products")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of available pages")
    items: List[ProductListItem] = Field(..., description="List of products")


class ProductDetail(ProductBase):
    """Detailed view for a single product."""

    categories_hierarchy: Optional[str] = Field(None, description="Category breadcrumb hierarchy")
    db_review_count: int = Field(0, description="Total customer reviews stored in platform")
    db_average_review_rating: Optional[float] = Field(None, description="Average rating computed from stored reviews")


class ProductStatistics(BaseModel):
    """Comprehensive rating statistics for a product based on stored reviews."""

    product_id: str = Field(..., description="Product ASIN")
    product_name: str = Field(..., description="Product name")
    total_reviews: int = Field(..., description="Total customer reviews in database")
    average_review_rating: Optional[float] = Field(None, description="Mean star rating of customer reviews")
    min_rating: Optional[float] = Field(None, description="Lowest review rating received")
    max_rating: Optional[float] = Field(None, description="Highest review rating received")
    verified_purchases_count: int = Field(0, description="Count of reviews marked as verified purchase")
    verified_purchases_percentage: float = Field(0.0, description="Percentage of verified reviews")
    star_distribution: List[RatingDistributionItem] = Field(..., description="Distribution across 1 to 5 stars")

