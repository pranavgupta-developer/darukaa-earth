"""
Project Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.project import ProjectType


class ProjectCreate(BaseModel):
    """Request schema for creating a project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    project_type: ProjectType


class ProjectUpdate(BaseModel):
    """Request schema for updating a project. All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    project_type: ProjectType | None = None


class ProjectResponse(BaseModel):
    """Response schema for a project."""

    id: uuid.UUID
    name: str
    description: str | None
    project_type: ProjectType
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    site_count: int = 0

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Response schema for a list of projects."""

    projects: list[ProjectResponse]
    total: int
