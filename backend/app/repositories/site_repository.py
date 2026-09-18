"""
Site repository — data-access layer for Site model.

Uses PostGIS functions for geometry storage and retrieval.
"""

import json
import uuid
from typing import Any

from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import Site


class SiteRepository:
    """Data-access operations for the Site model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        name: str,
        description: str | None,
        project_id: uuid.UUID,
        geojson: dict[str, Any],
        area_hectares: float | None,
    ) -> Site:
        """Create and persist a new site with PostGIS geometry."""
        geojson_str = json.dumps(geojson)
        site = Site(
            name=name,
            description=description,
            project_id=project_id,
            geometry=ST_GeomFromGeoJSON(geojson_str),
            area_hectares=area_hectares,
        )
        self.db.add(site)
        await self.db.commit()
        await self.db.refresh(site)
        return site

    async def get_by_id(self, site_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a site by ID with geometry as GeoJSON."""
        result = await self.db.execute(
            select(
                Site.id,
                Site.name,
                Site.description,
                Site.project_id,
                ST_AsGeoJSON(Site.geometry).label("geometry"),
                Site.area_hectares,
                Site.created_at,
                Site.updated_at,
            ).where(Site.id == site_id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return self._row_to_dict(row)

    async def list_by_project(self, project_id: uuid.UUID) -> list[dict[str, Any]]:
        """List all sites for a project with geometry as GeoJSON."""
        result = await self.db.execute(
            select(
                Site.id,
                Site.name,
                Site.description,
                Site.project_id,
                ST_AsGeoJSON(Site.geometry).label("geometry"),
                Site.area_hectares,
                Site.created_at,
                Site.updated_at,
            )
            .where(Site.project_id == project_id)
            .order_by(Site.created_at.desc())
        )
        return [self._row_to_dict(row) for row in result.all()]

    @staticmethod
    def _row_to_dict(row: Any) -> dict[str, Any]:
        """Convert a SQLAlchemy Row to a dict with parsed GeoJSON geometry."""
        return {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "project_id": row.project_id,
            "geometry": json.loads(row.geometry) if isinstance(row.geometry, str) else row.geometry,
            "area_hectares": row.area_hectares,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    async def get_model_by_id(self, site_id: uuid.UUID) -> Site | None:
        """Fetch a site by ID returning the SQLAlchemy model."""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        return result.scalar_one_or_none()

    async def update(self, site: Site, **kwargs: object) -> dict[str, Any] | None:
        """Update site fields."""
        if "geojson" in kwargs:
            geojson_str = json.dumps(kwargs.pop("geojson"))
            site.geometry = ST_GeomFromGeoJSON(geojson_str)
        for key, value in kwargs.items():
            if value is not None:
                setattr(site, key, value)
        await self.db.commit()
        return await self.get_by_id(site.id)

    async def delete(self, site: Site) -> None:
        """Delete a site."""
        await self.db.delete(site)
        await self.db.commit()
