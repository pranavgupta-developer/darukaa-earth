"""
Site API routes.

POST /api/projects/{project_id}/sites        — Create a site.
GET  /api/projects/{project_id}/sites        — List project sites.
GET  /api/projects/{project_id}/sites/geojson — Get sites as GeoJSON FeatureCollection.
GET  /api/sites/{site_id}                    — Get a site by ID.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.site import SiteCreate, SiteGeoJSONResponse, SiteListResponse, SiteResponse
from app.services.site_service import SiteService

router = APIRouter()


@router.post(
    "/projects/{project_id}/sites",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new site within a project",
)
async def create_site(
    project_id: uuid.UUID,
    data: SiteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SiteResponse:
    """Create a new geographical site with a GeoJSON polygon."""
    service = SiteService(db)
    return await service.create_site(project_id, data, current_user)


@router.get(
    "/projects/{project_id}/sites",
    response_model=SiteListResponse,
    summary="List all sites for a project",
)
async def list_sites(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SiteListResponse:
    """List all sites belonging to a project."""
    service = SiteService(db)
    return await service.list_sites(project_id, current_user)


@router.get(
    "/projects/{project_id}/sites/geojson",
    response_model=SiteGeoJSONResponse,
    summary="Get project sites as GeoJSON FeatureCollection",
)
async def get_sites_geojson(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SiteGeoJSONResponse:
    """Get all sites as a GeoJSON FeatureCollection for map rendering."""
    service = SiteService(db)
    return await service.get_sites_geojson(project_id, current_user)


@router.get(
    "/sites/{site_id}",
    response_model=SiteResponse,
    summary="Get a site by ID",
)
async def get_site(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SiteResponse:
    """Get a specific site. Requires project owner access."""
    service = SiteService(db)
    return await service.get_site(site_id, current_user)
