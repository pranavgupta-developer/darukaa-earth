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
from app.schemas.global_analytics import GlobalAnalyticsResponse, GlobalAnalyticsKPIs, ComparisonSeries

logger = get_logger(__name__)


class AnalyticsService:
    """Analytics business logic — aggregation, trends, and summary computation."""

    def __init__(self, db: AsyncSession) -> None:
        self.analytics_repo = AnalyticsRepository(db)
        self.site_repo = SiteRepository(db)
        self.project_repo = ProjectRepository(db)

    async def generate_mock_data_for_site(self, site_id: uuid.UUID) -> None:
        """Generate 24 months of mock analytics data for a specific site."""
        import math, random
        from datetime import date, timedelta
        from app.models.site_analytics import SiteAnalytics
        
        records: list[SiteAnalytics] = []
        today = date.today()
        start = today - timedelta(days=730)
        current = start

        base_ndvi = random.uniform(0.35, 0.55)
        base_carbon = random.uniform(1.0, 2.5)
        base_biodiversity = random.uniform(0.4, 0.6)
        base_canopy = random.uniform(40, 55)

        month_idx = 0
        while current <= today:
            seasonal = math.sin(2 * math.pi * (current.month - 3) / 12)
            ndvi = base_ndvi + 0.2 * seasonal + random.gauss(0, 0.03)
            ndvi = max(0.1, min(0.95, ndvi))

            carbon = base_carbon + 0.05 * month_idx + random.gauss(0, 0.2)
            carbon = max(0.1, carbon)

            biodiversity = base_biodiversity + random.gauss(0, 0.02)
            biodiversity = max(0.1, min(1.0, biodiversity))

            canopy = base_canopy + 0.3 * month_idx + random.gauss(0, 1.5)
            canopy = max(10, min(95, canopy))

            records.append(
                SiteAnalytics(
                    site_id=site_id,
                    recorded_date=current,
                    ndvi=round(ndvi, 4),
                    carbon_sequestration_tons=round(carbon, 2),
                    biodiversity_index=round(biodiversity, 4),
                    canopy_cover_pct=round(canopy, 1),
                )
            )
            current += timedelta(days=30)
            month_idx += 1

        self.analytics_repo.session.add_all(records)
        await self.analytics_repo.session.commit()

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

    async def get_global_analytics(
        self,
        user: User,
        project_ids: list[uuid.UUID] | None = None,
        site_ids: list[uuid.UUID] | None = None,
        project_types: list[str] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        compare_by: str = "site",
    ) -> GlobalAnalyticsResponse:
        """
        Aggregate and structure global analytics for cross-project comparison.
        """
        records = await self.analytics_repo.get_global_analytics(
            user_id=user.id,
            project_ids=project_ids,
            site_ids=site_ids,
            project_types=project_types,
            start_date=start_date,
            end_date=end_date,
        )

        if not records:
            return GlobalAnalyticsResponse(
                kpis=GlobalAnalyticsKPIs(
                    total_carbon_sequestered=0,
                    average_ndvi=0,
                    average_biodiversity=0,
                    average_canopy_cover=0,
                    total_monitored_area_ha=0,
                ),
                comparison_series=[],
            )

        # 1. Group records by comparison entity (site or project)
        series_map = {}
        distinct_sites = {}
        latest_carbon_by_site = {}

        for analytics, site, project in records:
            # Track distinct sites for area calculation and latest carbon
            distinct_sites[str(site.id)] = site.area_hectares or 0
            if analytics.carbon_sequestration_tons is not None:
                latest_carbon_by_site[str(site.id)] = analytics.carbon_sequestration_tons

            if compare_by == "project":
                entity_id = str(project.id)
                entity_name = project.name
            else:
                entity_id = str(site.id)
                entity_name = f"{project.name} - {site.name}"

            if entity_id not in series_map:
                series_map[entity_id] = {
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "data_points": []
                }

            series_map[entity_id]["data_points"].append(
                AnalyticsDataPoint(
                    recorded_date=analytics.recorded_date,
                    ndvi=analytics.ndvi,
                    carbon_sequestration_tons=analytics.carbon_sequestration_tons,
                    biodiversity_index=analytics.biodiversity_index,
                    canopy_cover_pct=analytics.canopy_cover_pct,
                )
            )

        # 2. Build comparison series
        comparison_series = []
        for entity_data in series_map.values():
            date_map = {}
            for dp in entity_data["data_points"]:
                d_str = dp.recorded_date.isoformat()
                if d_str not in date_map:
                    date_map[d_str] = {"ndvi": [], "carbon": [], "bio": [], "canopy": []}
                if dp.ndvi is not None: date_map[d_str]["ndvi"].append(dp.ndvi)
                if dp.carbon_sequestration_tons is not None: date_map[d_str]["carbon"].append(dp.carbon_sequestration_tons)
                if dp.biodiversity_index is not None: date_map[d_str]["bio"].append(dp.biodiversity_index)
                if dp.canopy_cover_pct is not None: date_map[d_str]["canopy"].append(dp.canopy_cover_pct)

            aggregated_data = []
            for d_str, vals in date_map.items():
                aggregated_data.append(AnalyticsDataPoint(
                    recorded_date=date.fromisoformat(d_str),
                    ndvi=sum(vals["ndvi"])/len(vals["ndvi"]) if vals["ndvi"] else None,
                    carbon_sequestration_tons=sum(vals["carbon"]) if vals["carbon"] else None,
                    biodiversity_index=sum(vals["bio"])/len(vals["bio"]) if vals["bio"] else None,
                    canopy_cover_pct=sum(vals["canopy"])/len(vals["canopy"]) if vals["canopy"] else None,
                ))
            
            # Sort by date
            aggregated_data.sort(key=lambda x: x.recorded_date)

            comparison_series.append(ComparisonSeries(
                entity_id=entity_data["entity_id"],
                entity_name=entity_data["entity_name"],
                data=aggregated_data,
            ))

        # 3. Calculate Global KPIs
        all_ndvi = [a.ndvi for a, s, p in records if a.ndvi is not None]
        all_bio = [a.biodiversity_index for a, s, p in records if a.biodiversity_index is not None]
        all_canopy = [a.canopy_cover_pct for a, s, p in records if a.canopy_cover_pct is not None]

        total_area = sum(distinct_sites.values())
        total_carbon = sum(latest_carbon_by_site.values())
        avg_ndvi = sum(all_ndvi) / len(all_ndvi) if all_ndvi else 0
        avg_bio = sum(all_bio) / len(all_bio) if all_bio else 0
        avg_canopy = sum(all_canopy) / len(all_canopy) if all_canopy else 0

        return GlobalAnalyticsResponse(
            kpis=GlobalAnalyticsKPIs(
                total_carbon_sequestered=round(total_carbon, 2),
                average_ndvi=round(avg_ndvi, 4),
                average_biodiversity=round(avg_bio, 4),
                average_canopy_cover=round(avg_canopy, 2),
                total_monitored_area_ha=round(total_area, 2),
            ),
            comparison_series=comparison_series,
        )
