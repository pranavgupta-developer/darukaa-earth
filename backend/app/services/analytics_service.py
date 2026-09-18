"""
Analytics service — business logic for site analytics.

Computes summary statistics and trends from time-series data.
Handles missing/incomplete data gracefully.
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.analytics import AnalyticsDataPoint, AnalyticsSummary, SiteAnalyticsResponse

logger = get_logger(__name__)


class AnalyticsService:
    """Analytics business logic — aggregation, trends, and summary computation."""

    def __init__(self, db: AsyncSession) -> None:
        self.analytics_repo = AnalyticsRepository(db)
        self.site_repo = SiteRepository(db)
        self.project_repo = ProjectRepository(db)

    async def get_site_analytics(
        self,
        site_id: uuid.UUID,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> SiteAnalyticsResponse:
        """
        Get analytics data for a site with summary statistics.

        Validates authorization via project ownership.
        Handles missing data by returning nulls — never fabricates values.
        """
        # Validate site exists
        site_data = await self.site_repo.get_by_id(site_id)
        if site_data is None:
            raise NotFoundError("Site", str(site_id))

        # Validate project ownership
        project = await self.project_repo.get_by_id(site_data["project_id"])
        if project is None:
            raise NotFoundError("Project", str(site_data["project_id"]))
        if project.owner_id != user.id:
            raise AuthorizationError("Not authorized to access this site's analytics")

        # Fetch time-series data
        records = await self.analytics_repo.get_by_site(site_id, start_date, end_date)

        data_points = [
            AnalyticsDataPoint(
                recorded_date=r.recorded_date,
                ndvi=r.ndvi,
                carbon_sequestration_tons=r.carbon_sequestration_tons,
                biodiversity_index=r.biodiversity_index,
                canopy_cover_pct=r.canopy_cover_pct,
            )
            for r in records
        ]

        # Compute summaries per metric
        summary = {
            "ndvi": self._compute_summary([d.ndvi for d in data_points]),
            "carbon_sequestration_tons": self._compute_summary(
                [d.carbon_sequestration_tons for d in data_points]
            ),
            "biodiversity_index": self._compute_summary(
                [d.biodiversity_index for d in data_points]
            ),
            "canopy_cover_pct": self._compute_summary(
                [d.canopy_cover_pct for d in data_points]
            ),
        }

        return SiteAnalyticsResponse(
            site_id=site_id,
            site_name=site_data["name"],
            start_date=data_points[0].recorded_date if data_points else None,
            end_date=data_points[-1].recorded_date if data_points else None,
            total_records=len(data_points),
            data=data_points,
            summary=summary,
        )

    @staticmethod
    def _compute_summary(values: list[float | None]) -> AnalyticsSummary:
        """
        Compute summary statistics for a metric.

        Filters out None values. Returns empty summary if no valid data.
        """
        valid = [v for v in values if v is not None]

        if not valid:
            return AnalyticsSummary()

        latest = valid[-1]
        avg = sum(valid) / len(valid)
        min_val = min(valid)
        max_val = max(valid)

        # Trend: percentage change from first to last valid value
        trend = None
        if len(valid) >= 2 and valid[0] != 0:
            trend = round(((valid[-1] - valid[0]) / abs(valid[0])) * 100, 2)

        return AnalyticsSummary(
            latest_value=round(latest, 4),
            average=round(avg, 4),
            min_value=round(min_val, 4),
            max_value=round(max_val, 4),
            trend_pct=trend,
        )
