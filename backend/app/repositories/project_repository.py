"""
Project repository — data-access layer for Project model.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.site import Site


class ProjectRepository:
    """Data-access operations for the Project model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, name: str, description: str | None, project_type: str, owner_id: uuid.UUID) -> Project:
        """Create and persist a new project."""
        project = Project(
            name=name,
            description=description,
            project_type=project_type,
            owner_id=owner_id,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Fetch a project by ID."""
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: uuid.UUID) -> list[Project]:
        """List all projects owned by a user."""
        result = await self.db.execute(
            select(Project).where(Project.owner_id == owner_id).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, project: Project, **kwargs: object) -> Project:
        """Update project fields."""
        for key, value in kwargs.items():
            if value is not None:
                setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_site_count(self, project_id: uuid.UUID) -> int:
        """Get the number of sites in a project."""
        result = await self.db.execute(
            select(func.count(Site.id)).where(Site.project_id == project_id)
        )
        return result.scalar_one()
