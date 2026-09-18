"""
Project SQLAlchemy model.

Represents a carbon/biodiversity project owned by an authenticated user.
"""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ProjectType(str, PyEnum):
    """Controlled enum for project categories."""

    CARBON_SEQUESTRATION = "Carbon Sequestration"
    BIODIVERSITY_CONSERVATION = "Biodiversity Conservation"
    REFORESTATION = "Reforestation"


class Project(UUIDMixin, TimestampMixin, Base):
    """Carbon/biodiversity project."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_type: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType, name="project_type_enum", create_type=True, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    owner: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="projects"
    )
    sites: Mapped[list["Site"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Site", back_populates="project", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name}>"
