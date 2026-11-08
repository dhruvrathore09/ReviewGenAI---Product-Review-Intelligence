"""API route definitions package."""

from src.api.routes.health import router as health_router
from src.api.routes.products import router as products_router
from src.api.routes.reviews import router as reviews_router
from src.api.routes.dashboard import router as dashboard_router

__all__ = ["health_router", "products_router", "reviews_router", "dashboard_router"]

