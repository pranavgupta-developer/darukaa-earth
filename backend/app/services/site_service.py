"""
Site service — business logic for geospatial site management.

Orchestrates:
- Authorization (project owner check)
- Project existence validation
- GeoJSON geometry validation
- Area calculation
- Site persistence
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.site import SiteCreate, SiteGeoJSONResponse, SiteListResponse, SiteResponse
from app.services.geospatial_validator import validate_geojson_geometry

logger = get_logger(__name__)

# Approximate conversion factor for sq degrees to hectares at equator
# More accurate per-site with proper projection, but sufficient for mock/display
SQ_DEGREE_TO_HECTARES = 12_363.0


class SiteService:
    """Site management business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.site_repo = SiteRepository(db)
        self.project_repo = ProjectRepository(db)

    async def _validate_project_access(
        self, project_id: uuid.UUID, user: User
    ) -> None:
        """Validate project exists and user is the owner."""
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))
        if project.owner_id != user.id:
            raise AuthorizationError("Not authorized to access this project")

    async def create_site(
        self, project_id: uuid.UUID, data: SiteCreate, user: User
    ) -> SiteResponse:
        """
        Create a new site within a project.

        Validates project access, GeoJSON geometry, and persists via PostGIS.
        """
        await self._validate_project_access(project_id, user)

        # Validate geometry — raises GeospatialValidationError on failure
        polygon = validate_geojson_geometry(data.geometry)

        # Calculate approximate area in hectares
        area_hectares = polygon.area * SQ_DEGREE_TO_HECTARES

        site_dict = await self.site_repo.create(
            name=data.name,
            description=data.description,
            project_id=project_id,
            geojson=data.geometry,
            area_hectares=round(area_hectares, 2),
        )

        # Refetch to get GeoJSON from PostGIS
        site_data = await self.site_repo.get_by_id(site_dict.id)
        if site_data is None:
            # Should not happen — defensive coding
            raise NotFoundError("Site", str(site_dict.id))

        logger.info("Site created: %s in project %s", site_data["id"], project_id)
        
        # Generate mock analytics data for the new site automatically
        try:
            from app.services.analytics_service import AnalyticsService
            analytics_svc = AnalyticsService(self.site_repo.session)
            # site_dict.id is the UUID of the newly created site
            await analytics_svc.generate_mock_data_for_site(site_dict.id)
            logger.info("Mock analytics generated for site: %s", site_dict.id)
        except Exception as e:
            logger.error("Failed to generate mock analytics for site %s: %s", site_dict.id, e)

        return SiteResponse(**site_data)

    async def list_sites(
        self, project_id: uuid.UUID, user: User
    ) -> SiteListResponse:
        """List all sites for a project."""
        await self._validate_project_access(project_id, user)
        sites = await self.site_repo.list_by_project(project_id)
        return SiteListResponse(
            sites=[SiteResponse(**s) for s in sites],
            total=len(sites),
        )

    async def get_site(self, site_id: uuid.UUID, user: User) -> SiteResponse:
        """Get a site by ID with authorization check."""
        site_data = await self.site_repo.get_by_id(site_id)
        if site_data is None:
            raise NotFoundError("Site", str(site_id))

        # Check authorization via project ownership
        await self._validate_project_access(site_data["project_id"], user)
        return SiteResponse(**site_data)

    async def get_sites_geojson(
        self, project_id: uuid.UUID, user: User
    ) -> SiteGeoJSONResponse:
        """
        Get all sites for a project as a GeoJSON FeatureCollection.

        Optimized for Mapbox GL JS map rendering.
        """
        await self._validate_project_access(project_id, user)
        sites = await self.site_repo.list_by_project(project_id)

        features: list[dict[str, Any]] = []
        for site in sites:
            feature = {
                "type": "Feature",
                "id": str(site["id"]),
                "geometry": site["geometry"],
                "properties": {
                    "id": str(site["id"]),
                    "name": site["name"],
                    "description": site["description"],
                    "area_hectares": site["area_hectares"],
                    "project_id": str(site["project_id"]),
                },
            }
        return SiteGeoJSONResponse(features=features)

    async def update_site(
        self, site_id: uuid.UUID, data: Any, user: User
    ) -> SiteResponse:
        """Update a site."""
        site = await self.site_repo.get_model_by_id(site_id)
        if site is None:
            raise NotFoundError("Site", str(site_id))

        await self._validate_project_access(site.project_id, user)

        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.description is not None:
            update_data["description"] = data.description
        if data.geometry is not None:
            polygon = validate_geojson_geometry(data.geometry)
            update_data["geojson"] = data.geometry
            update_data["area_hectares"] = round(polygon.area * SQ_DEGREE_TO_HECTARES, 2)

        site_data = await self.site_repo.update(site, **update_data)
        if site_data is None:
            raise NotFoundError("Site", str(site_id))
            
        logger.info("Site updated: %s", site_id)
        return SiteResponse(**site_data)

    async def delete_site(self, site_id: uuid.UUID, user: User) -> None:
        """Delete a site."""
        site = await self.site_repo.get_model_by_id(site_id)
        if site is None:
            raise NotFoundError("Site", str(site_id))

        await self._validate_project_access(site.project_id, user)
        
        await self.site_repo.delete(site)
        logger.info("Site deleted: %s", site_id)
