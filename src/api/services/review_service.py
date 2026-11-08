"""Service layer for review querying, filtering, and pagination."""

import math
from typing import Optional
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import Session

from src.db.models import Product, Review
from src.api.schemas.review import ReviewItem, ReviewListResponse


class ReviewService:
    """Encapsulates review business logic and database queries."""

    @staticmethod
    def get_product_reviews(
        db: Session,
        product_id: str,
        page: int = 1,
        page_size: int = 20,
        star_rating: Optional[float] = None,
        verified_only: Optional[bool] = None,
        sort_by: str = "date",
        order: str = "desc",
    ) -> Optional[ReviewListResponse]:
        """Fetch paginated, filtered, and sorted reviews for a specified product.
        
        Returns None if product_id does not exist.
        """
        # Ensure product exists
        product = db.get(Product, product_id)
        if not product:
            return None

        stmt = select(Review).where(Review.product_id == product_id)

        # Filters
        if star_rating is not None:
            stmt = stmt.where(Review.star_rating == star_rating)
        if verified_only is not None and verified_only:
            stmt = stmt.where(Review.verified_purchase == True)

        # Total matching reviews
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        # Sorting
        sort_map = {
            "date": Review.review_date,
            "rating": Review.star_rating,
            "helpful": Review.helpful_votes,
            "helpful_votes": Review.helpful_votes,
        }
        target_col = sort_map.get(sort_by, Review.review_date)

        if order.lower() == "asc":
            stmt = stmt.order_by(asc(target_col), asc(Review.review_id))
        else:
            stmt = stmt.order_by(desc(target_col), desc(Review.review_id))

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        records = db.scalars(stmt).all()

        items = [
            ReviewItem(
                review_id=r.review_id,
                product_id=r.product_id,
                user_id=r.user_id,
                review_title=r.review_title,
                review_text=r.review_text,
                star_rating=float(r.star_rating),
                review_timestamp=r.review_timestamp,
                review_date=r.review_date,
                helpful_votes=r.helpful_votes,
                verified_purchase=r.verified_purchase,
            )
            for r in records
        ]

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return ReviewListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=items,
        )

