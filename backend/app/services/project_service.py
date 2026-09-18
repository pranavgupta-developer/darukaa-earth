"""
Project service — business logic for project management.

Enforces authorization (owner-only access) and orchestrates repository calls.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.logging import get_logger
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate

logger = get_logger(__name__)


class ProjectService:
    """Project management business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = ProjectRepository(db)

    async def _to_response(self, project: Project) -> ProjectResponse:
        """Convert a Project model to a response schema with site count."""
        site_count = await self.repo.get_site_count(project.id)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            owner_id=project.owner_id,
            created_at=project.created_at,
            updated_at=project.updated_at,
            site_count=site_count,
        )

    async def create_project(self, data: ProjectCreate, owner: User) -> ProjectResponse:
        """Create a new project owned by the authenticated user."""
        project = await self.repo.create(
            name=data.name,
            description=data.description,
            project_type=data.project_type.value,
            owner_id=owner.id,
        )
        logger.info("Project created: %s by user %s", project.id, owner.id)
        return await self._to_response(project)

    async def list_projects(self, owner: User) -> ProjectListResponse:
        """List all projects owned by the authenticated user."""
        projects = await self.repo.list_by_owner(owner.id)
        responses = [await self._to_response(p) for p in projects]
        return ProjectListResponse(projects=responses, total=len(responses))

    async def get_project(self, project_id: uuid.UUID, user: User) -> ProjectResponse:
        """
        Get a project by ID. Enforces owner-only access.

        Raises:
            NotFoundError: If project doesn't exist.
            AuthorizationError: If user is not the project owner.
        """
        project = await self.repo.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))
        if project.owner_id != user.id:
            raise AuthorizationError("Not authorized to access this project")
        return await self._to_response(project)

    async def update_project(
        self, project_id: uuid.UUID, data: ProjectUpdate, user: User
    ) -> ProjectResponse:
        """
        Update a project. Enforces owner-only access.

        Raises:
            NotFoundError: If project doesn't exist.
            AuthorizationError: If user is not the project owner.
        """
        project = await self.repo.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))
        if project.owner_id != user.id:
            raise AuthorizationError("Not authorized to modify this project")

        update_data = data.model_dump(exclude_unset=True)
        if "project_type" in update_data and update_data["project_type"] is not None:
            update_data["project_type"] = update_data["project_type"].value

        project = await self.repo.update(project, **update_data)
        logger.info("Project updated: %s", project.id)
        return await self._to_response(project)
