"""FastAPI application initialization and router configuration."""

import logging
import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from src.api.routes.health import router as health_router
from src.api.routes.products import router as products_router
from src.api.routes.reviews import router as reviews_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.assistant import router as assistant_router
from src.db.seed_all import seed_database

logger = logging.getLogger(__name__)


def background_seed():
    try:
        seed_database()
    except Exception as e:
        logger.warning("Auto-seed background job completed or skipped: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed blank databases in production
    threading.Thread(target=background_seed, daemon=True).start()
    yield


def create_app() -> FastAPI:
    """Application factory for the Product Review Intelligence Platform API."""
    app = FastAPI(
        title="Product Review Intelligence Platform API",
        description=(
            "REST API providing product discovery, customer review inspection, "
            "and rating statistics powered by PostgreSQL and the Amazon Reviews 2023 dataset."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS for local development and cloud deployments (Vercel, Render, Railway, Netlify)
    cors_env = os.getenv("CORS_ORIGINS", "")
    allowed_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        *allowed_origins,
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if (origins and "*" not in origins) else ["*"],
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routers with common '/api' prefix
    app.include_router(health_router, prefix="/api")
    app.include_router(products_router, prefix="/api")
    app.include_router(reviews_router, prefix="/api")
    app.include_router(dashboard_router, prefix="/api")
    app.include_router(assistant_router, prefix="/api")

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Sanitize unhandled internal exceptions to prevent credential or trace leakage."""
        logger.error("Unhandled server exception at %s: %s", request.url, exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."},
        )

    @app.get("/", include_in_schema=False)
    def root_redirect():
        """Redirect base URL to Swagger interactive documentation."""
        return RedirectResponse(url="/docs")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

