"""
Analytics API routes.

GET /api/sites/{site_id}/analytics — Get site analytics time-series with optional date filters.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import SiteAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "/sites/{site_id}/analytics",
    response_model=SiteAnalyticsResponse,
    summary="Get site analytics time-series data",
)
async def get_site_analytics(
    site_id: uuid.UUID,
    start_date: date | None = Query(None, description="Filter start date (inclusive)"),
    end_date: date | None = Query(None, description="Filter end date (inclusive)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SiteAnalyticsResponse:
    """Get analytics data for a site with summary statistics and trends."""
    service = AnalyticsService(db)
    return await service.get_site_analytics(site_id, current_user, start_date, end_date)
