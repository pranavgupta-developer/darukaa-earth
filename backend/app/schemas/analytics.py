"""
Analytics Pydantic schemas for request/response validation.

Structured for extensibility — a real data provider can replace the
mock data by implementing the same response contracts.
"""

import uuid
from datetime import date

from pydantic import BaseModel


class AnalyticsDataPoint(BaseModel):
    """A single time-series data point."""

    recorded_date: date
    ndvi: float | None = None
    carbon_sequestration_tons: float | None = None
    biodiversity_index: float | None = None
    canopy_cover_pct: float | None = None

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    """Summary statistics for a metric."""

    latest_value: float | None = None
    average: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    trend_pct: float | None = None  # % change from first to last data point


class SiteAnalyticsResponse(BaseModel):
    """Complete analytics response for a site."""

    site_id: uuid.UUID
    site_name: str
    start_date: date | None = None
    end_date: date | None = None
    total_records: int
    data: list[AnalyticsDataPoint]
    summary: dict[str, AnalyticsSummary]
