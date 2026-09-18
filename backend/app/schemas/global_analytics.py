"""
Global Analytics Pydantic schemas.
"""

from datetime import date
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.schemas.analytics import AnalyticsDataPoint, AnalyticsSummary

class GlobalAnalyticsKPIs(BaseModel):
    """Aggregated KPIs across all selected projects and sites."""
    total_carbon_sequestered: float
    average_ndvi: float
    average_biodiversity: float
    average_canopy_cover: float
    total_monitored_area_ha: float

class ComparisonSeries(BaseModel):
    """A time-series data set for a single project or site."""
    entity_id: str
    entity_name: str
    data: List[AnalyticsDataPoint]

class GlobalAnalyticsResponse(BaseModel):
    """Response schema for global analytics."""
    kpis: GlobalAnalyticsKPIs
    comparison_series: List[ComparisonSeries]
