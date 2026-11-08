"""Pydantic schemas for executive product intelligence and review reports."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AspectDetail(BaseModel):
    """Detailed rating and analysis for a single product dimension (e.g. Durability, Battery Life)."""

    name: str = Field(..., description="Aspect name (e.g. Durability & Build Quality)")
    score: float = Field(..., description="Computed honest aspect rating out of 5.0")
    percentage: float = Field(..., description="Score converted to percentage (0-100%)")
    status: str = Field(..., description="Status badge (e.g. Exceptional, Solid, Caution, Trade-Off)")
    summary: str = Field(..., description="Synthesized review consensus for this aspect")
    key_evidence: str = Field(..., description="Supporting evidence or specific finding from reviews")


class CriticalNegativePoint(BaseModel):
    """Specific honest negative point, flaw, or buyer warning."""

    title: str = Field(..., description="Flaw title (e.g. Battery Degradation & High Drain)")
    severity: str = Field(..., description="Severity level: High, Medium, or Moderate")
    description: str = Field(..., description="Detailed explanation of reported failure or deficiency")
    quote: Optional[str] = Field(None, description="Direct quote from 1-star or 2-star customer reviews")


class ProductIntelligenceReport(BaseModel):
    """Comprehensive executive intelligence report synthesizing customer reviews for a product."""

    product_id: str = Field(..., description="Unique product ASIN")
    product_name: str = Field(..., description="Product title / name")
    brand: Optional[str] = Field(None, description="Manufacturer or brand")
    main_category: Optional[str] = Field(None, description="Primary product category")
    price: Optional[float] = Field(None, description="Listing price in USD")
    image_url: Optional[str] = Field(None, description="Primary product image URL")

    # Ratings: Listed Marketplace vs Honest Reality Rating
    marketplace_listed_rating: Optional[float] = Field(None, description="Raw Amazon marketplace rating")
    overall_rating: float = Field(..., description="Honest, reality-checked rating penalizing for defects (out of 5.0)")
    total_ratings_count: int = Field(..., description="Total verified ratings and customer reviews")
    satisfaction_rate: float = Field(..., description="True satisfaction rate reflecting critical reviews (0-100%)")
    critical_complaint_rate: float = Field(..., description="Percentage of reviews reporting critical defects or returns")
    quality_grade: str = Field(..., description="Honest grade badge: A, B+, B, C+, C, D")
    confidence_level: str = Field(..., description="Confidence assessment based on sample size")

    # Executive Overview
    executive_summary: str = Field(..., description="Comprehensive synthesized consensus paragraph")
    overall_verdict: str = Field(..., description="Honest, realistic bottom-line verdict for buyers")

    # Critical Negative Points & Real Negative Quotes (Highlighted prominently!)
    critical_negative_points: List[CriticalNegativePoint] = Field(..., description="Confirmed negative points, defects, and dealbreakers")
    real_negative_quotes: List[str] = Field(default_factory=list, description="Direct quotes from real 1-star and 2-star buyer reviews")

    # Core Dimensions (Durability, Lifespan/Battery, Performance, Usability, Value)
    aspects: List[AspectDetail] = Field(..., description="Detailed breakdown of core product dimensions")

    # Detailed Intelligence Findings
    strengths: List[str] = Field(..., description="Confirmed positive strengths reported by owners")
    flaws_and_drawbacks: List[str] = Field(..., description="Confirmed drawbacks, failure points, or caveats")
    durability_and_longevity_deep_dive: str = Field(..., description="Dedicated deep dive into physical build, materials, and long-term lifespan")
    who_should_buy: str = Field(..., description="Specific recommendation on who this product is suited for")
    who_should_skip: str = Field(..., description="Specific warning on who should avoid or look for alternatives")
