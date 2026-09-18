"""
Site Pydantic schemas for request/response validation.

Uses GeoJSON Feature format for the API contract:
- Input: GeoJSON geometry object + site metadata
- Output: GeoJSON-compatible geometry + site metadata
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    """
    Request schema for creating a site.

    The geometry field accepts a GeoJSON Geometry object:
    {
        "type": "Polygon",
        "coordinates": [[[lng, lat], [lng, lat], ...]]
    }
    """

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    geometry: dict[str, Any] = Field(
        ...,
        description="GeoJSON Polygon geometry object",
        json_schema_extra={
            "example": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [77.5946, 12.9716],
                        [77.5950, 12.9720],
                        [77.5955, 12.9716],
                        [77.5946, 12.9716],
                    ]
                ],
            }
        },
    )


class SiteResponse(BaseModel):
    """Response schema for a site with GeoJSON geometry."""

    id: uuid.UUID
    name: str
    description: str | None
    project_id: uuid.UUID
    geometry: dict[str, Any]
    area_hectares: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SiteListResponse(BaseModel):
    """Response schema for a list of sites."""

    sites: list[SiteResponse]
    total: int


class SiteGeoJSONResponse(BaseModel):
    """GeoJSON FeatureCollection response for map rendering."""

    type: str = "FeatureCollection"
    features: list[dict[str, Any]]
