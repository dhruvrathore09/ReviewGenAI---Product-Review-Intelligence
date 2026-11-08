"""Pydantic schemas for platform-level dashboard metrics."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.api.schemas.product import RatingDistributionItem


class CategoryBenchmarkItem(BaseModel):
    """Deep category intelligence benchmarks including aspects, complaints, and leaders."""

    category: str = Field(..., description="Category name")
    product_count: int = Field(..., description="Number of catalog items")
    review_count: int = Field(..., description="Number of customer reviews")
    avg_rating: float = Field(..., description="Category mean rating")
    satisfaction_rate: float = Field(..., description="Satisfaction rate percentage")
    durability_score: float = Field(..., description="Durability index out of 5.0")
    battery_score: float = Field(..., description="Battery/Lifespan index out of 5.0")
    performance_score: float = Field(..., description="Performance index out of 5.0")
    value_score: float = Field(..., description="Value for money index out of 5.0")
    top_complaints: List[Dict[str, Any]] = Field(..., description="Top failure points and complaint ratios")
    top_products: List[Dict[str, Any]] = Field(..., description="Top verified models in this category")
    tiered_products: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        default=None,
        description="Products grouped across rating tiers (5_star, 4_star, 3_star, 1_2_star)",
    )


class ComparatorProductItem(BaseModel):
    """Product summary for comparator selection dropdowns."""

    product_id: str = Field(..., description="Unique product identifier (ASIN)")
    product_name: str = Field(..., description="Full product title")
    brand: Optional[str] = Field(None, description="Manufacturer brand name")
    price: Optional[float] = Field(None, description="Listing price in USD")
    average_rating: Optional[float] = Field(None, description="Amazon catalog average rating")
    honest_rating: Optional[float] = Field(None, description="Calculated honest reality rating")
    rating_number: Optional[int] = Field(None, description="Total ratings count")
    image_url: Optional[str] = Field(None, description="Primary product image URL")


class ComparisonItem(BaseModel):
    """Head-to-head comparison between two real products."""

    id: str = Field(..., description="Comparison identifier")
    title: str = Field(..., description="Matchup headline (e.g. Flagship Headphones Duel)")
    category: str = Field(..., description="Category name")
    product_a: Dict[str, Any] = Field(..., description="Specs and scores for Product A")
    product_b: Dict[str, Any] = Field(..., description="Specs and scores for Product B")
    winner_summary: str = Field(..., description="Executive verdict and winner analysis")


class MarketFlawItem(BaseModel):
    """Reliability failure radar item."""

    category: str = Field(..., description="Defect/complaint domain")
    failure_percentage: float = Field(..., description="Share of critical negative reviews")
    description: str = Field(..., description="Detailed explanation of failure mode")


class AnalyticsHubResponse(BaseModel):
    """Complete response for the upgraded Review Analytics Hub."""

    categories: List[CategoryBenchmarkItem] = Field(..., description="Category-specific intelligence benchmarks")
    comparisons: List[ComparisonItem] = Field(..., description="Head-to-head product comparisons")
    market_flaws: List[MarketFlawItem] = Field(..., description="Market-wide failure and defect radar")


class CategoryOverviewItem(BaseModel):
    """Aggregate product and review statistics per category."""

    category: str = Field(..., description="Category name")
    product_count: int = Field(..., description="Number of products in category")
    review_count: int = Field(0, description="Total reviews in category")


class BrandOverviewItem(BaseModel):
    """Aggregate statistics per brand."""

    brand: str = Field(..., description="Brand name")
    product_count: int = Field(..., description="Number of products manufactured")
    average_rating: Optional[float] = Field(None, description="Average catalog rating")


class DashboardOverviewResponse(BaseModel):
    """Platform-wide summary metrics for home and analytics overview."""

    total_products: int = Field(..., description="Total unique products in catalog")
    total_reviews: int = Field(..., description="Total verified customer reviews in database")
    overall_average_review_rating: float = Field(..., description="Mean rating across all customer reviews")
    total_verified_reviews: int = Field(..., description="Count of reviews from verified purchases")
    verified_reviews_percentage: float = Field(..., description="Percentage of verified reviews")
    rating_distribution: List[RatingDistributionItem] = Field(..., description="Global rating distribution across 1-5 stars")
    top_categories: List[CategoryOverviewItem] = Field(..., description="Top product categories by volume")
    top_brands: List[BrandOverviewItem] = Field(..., description="Top product brands by volume")

