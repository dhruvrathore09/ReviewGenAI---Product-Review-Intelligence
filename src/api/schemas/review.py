"""Pydantic schemas for review-related endpoints."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewItem(BaseModel):
    """Schema representing an individual customer review."""

    review_id: int = Field(..., description="Unique review identifier")
    product_id: str = Field(..., description="Target product ASIN")
    user_id: Optional[str] = Field(None, description="Anonymized reviewer ID")
    review_title: Optional[str] = Field(None, description="Review headline")
    review_text: str = Field(..., description="Original raw customer review body")
    star_rating: float = Field(..., description="Numerical star rating (1.0 to 5.0)")
    review_timestamp: int = Field(..., description="Epoch timestamp in milliseconds")
    review_date: datetime = Field(..., description="ISO formatted review submission datetime")
    helpful_votes: int = Field(0, description="Helpful votes count")
    verified_purchase: bool = Field(False, description="Verified purchase status")

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    """Paginated review collection response."""

    total: int = Field(..., description="Total matching reviews count")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Reviews per page")
    total_pages: int = Field(..., description="Total available pages")
    items: List[ReviewItem] = Field(..., description="List of review records")

