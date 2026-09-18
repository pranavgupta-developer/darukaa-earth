"""
Darukaa.Earth — FastAPI Application Factory.

Configures CORS, mounts API routers, and registers exception handlers.
This is the ASGI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    setup_logging()

    app = FastAPI(
        title="Darukaa.Earth API",
        description="Geospatial data analytics platform for carbon and biodiversity projects",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — allow configured frontend origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # API routers — imported here to avoid circular imports
    from app.api.routes.auth import router as auth_router
    from app.api.routes.projects import router as projects_router
    from app.api.routes.sites import router as sites_router
    from app.api.routes.analytics import router as analytics_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
    app.include_router(sites_router, prefix="/api", tags=["Sites"])
    app.include_router(analytics_router, prefix="/api", tags=["Analytics"])

    @app.get("/api/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint for deployment probes."""
        return {"status": "healthy"}

    return app


app = create_app()
