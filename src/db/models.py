"""SQLAlchemy ORM models for the Product Review Intelligence Platform."""

from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    """Product model storing catalog metadata."""

    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, nullable=False, comment="Unique ASIN / product identifier")
    product_name = Column(Text, nullable=False, comment="Official product title / name")
    main_category = Column(String(100), nullable=True, comment="Primary product category")
    categories_hierarchy = Column(Text, nullable=True, comment="JSON representation or breadcrumb hierarchy of categories")
    price = Column(Numeric(10, 2), nullable=True, comment="Product retail price in USD")
    brand = Column(String(255), nullable=True, comment="Product manufacturer or brand name")
    image_url = Column(Text, nullable=True, comment="Primary product image URL")
    average_rating = Column(Numeric(3, 2), nullable=True, comment="Aggregated average star rating (0.00 - 5.00)")
    rating_number = Column(Integer, nullable=True, default=0, comment="Total count of customer ratings received")

    # Relationship to reviews
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        Index("idx_products_brand", "brand"),
        Index("idx_products_main_category", "main_category"),
        CheckConstraint(
            "average_rating IS NULL OR (average_rating >= 0.0 AND average_rating <= 5.0)",
            name="chk_products_avg_rating_range",
        ),
    )

    def __repr__(self) -> str:
        return f"<Product(product_id='{self.product_id}', name='{self.product_name[:30]}...', price={self.price})>"


class Review(Base):
    """Customer review model storing verified feedback, ratings, and timestamps."""

    __tablename__ = "reviews"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="Auto-incrementing surrogate primary key")
    product_id = Column(
        String(50),
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Foreign key referencing products.product_id",
    )
    user_id = Column(String(100), nullable=True, comment="Unique anonymized reviewer ID")
    review_title = Column(Text, nullable=True, comment="Customer review headline / title")
    review_text = Column(Text, nullable=False, comment="Full original customer review text")
    star_rating = Column(Numeric(2, 1), nullable=False, comment="Review star rating (1.0 - 5.0)")
    review_timestamp = Column(BigInteger, nullable=False, comment="Unix epoch timestamp in milliseconds")
    review_date = Column(DateTime, nullable=False, comment="Parsed ISO/UTC datetime of review submission")
    helpful_votes = Column(Integer, nullable=False, default=0, comment="Number of helpful votes by other customers")
    verified_purchase = Column(Boolean, nullable=False, default=False, comment="Whether the review was a verified purchase")

    # Relationship back to product
    product = relationship("Product", back_populates="reviews")

    __table_args__ = (
        Index("idx_reviews_product_id", "product_id"),
        Index("idx_reviews_star_rating", "star_rating"),
        Index("idx_reviews_review_date", "review_date"),
        UniqueConstraint("product_id", "user_id", "review_timestamp", name="uq_reviews_product_user_timestamp"),
        CheckConstraint("star_rating >= 1.0 AND star_rating <= 5.0", name="chk_reviews_star_rating_range"),
    )

    def __repr__(self) -> str:
        return (
            f"<Review(review_id={self.review_id}, product_id='{self.product_id}', "
            f"rating={self.star_rating}, date='{self.review_date}')>"
        )

