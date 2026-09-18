"""
Analytics repository — data-access layer for SiteAnalytics model.

Queries time-series data with optional date-range filtering.
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_analytics import SiteAnalytics


class AnalyticsRepository:
    """Data-access operations for the SiteAnalytics model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_site(
        self,
        site_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[SiteAnalytics]:
        """
        Query analytics time-series data for a site.

        Args:
            site_id: The site to query.
            start_date: Optional start date filter (inclusive).
            end_date: Optional end date filter (inclusive).

        Returns:
            List of SiteAnalytics records ordered by date ascending.
        """
        query = (
            select(SiteAnalytics)
            .where(SiteAnalytics.site_id == site_id)
            .order_by(SiteAnalytics.recorded_date.asc())
        )

        if start_date is not None:
            query = query.where(SiteAnalytics.recorded_date >= start_date)
        if end_date is not None:
            query = query.where(SiteAnalytics.recorded_date <= end_date)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_bulk(self, records: list[SiteAnalytics]) -> None:
        """Bulk insert analytics records (used by seed script)."""
        self.db.add_all(records)
        await self.db.commit()
