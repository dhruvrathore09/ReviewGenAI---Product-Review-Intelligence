"""Pydantic schemas for the AI Review Intelligence Assistant."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message within the conversational thread."""
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message in Markdown")


class ChatRequest(BaseModel):
    """Request payload sent by the chat UI."""
    messages: List[ChatMessage] = Field(..., description="Chronological conversation message history")
    query: Optional[str] = Field(None, description="Current message text if not appended to messages array")


class ProductCardSummary(BaseModel):
    """Structured summary card of a product cited in the assistant response."""
    product_id: str = Field(..., description="Amazon ASIN")
    product_name: str = Field(..., description="Cleaned product title")
    brand: Optional[str] = Field(None, description="Canonical brand name")
    price: Optional[float] = Field(None, description="Listing price in USD")
    image_url: Optional[str] = Field(None, description="Product image URL")
    honest_rating: float = Field(..., description="Debiased honest rating out of 5.0")
    marketplace_rating: Optional[float] = Field(None, description="Raw Amazon catalog rating")
    quality_grade: str = Field(..., description="Quality grade: A+, A, B+, B, C, D")
    critical_complaint_rate: float = Field(..., description="Percentage of reviews reporting critical flaws")
    highlight: Optional[str] = Field(None, description="Key takeaway or trade-off")


class SourceCitation(BaseModel):
    """Verifiable data provenance citation linking assistant claims to customer reviews."""
    product_id: str = Field(..., description="Cited product ASIN")
    product_name: str = Field(..., description="Product title")
    total_reviews_analyzed: int = Field(..., description="Count of customer reviews processed for this citation")
    verified_purchases_ratio: float = Field(..., description="Percentage of verified purchases in sample")
    key_aspect: Optional[str] = Field(None, description="Primary aspect evaluated (e.g. Battery, Durability)")


class ChatResponse(BaseModel):
    """Response payload returned to the conversational UI."""
    reply: str = Field(..., description="Synthesized Markdown response")
    products: List[ProductCardSummary] = Field(default_factory=list, description="Products referenced in the answer")
    suggested_followups: List[str] = Field(default_factory=list, description="Context-aware suggested follow-up questions")
    sources: List[SourceCitation] = Field(default_factory=list, description="Audit citations from PostgreSQL review records")
    intent: str = Field(default="general", description="Detected query intent archetype")


class StarterPrompt(BaseModel):
    """Pre-curated prompt suggestions for new chat sessions."""
    category: str
    icon: str
    title: str
    prompt: str
