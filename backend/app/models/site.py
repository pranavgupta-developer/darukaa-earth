"""
Site SQLAlchemy model with PostGIS geometry column.

Stores geographical site polygons associated with projects.
Includes a spatial index for efficient geospatial queries.
"""

import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Site(UUIDMixin, TimestampMixin, Base):
    """Geographical site with a PostGIS polygon geometry."""

    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    geometry: Mapped[str] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
        nullable=False,
    )
    area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Project", back_populates="sites"
    )
    analytics: Mapped[list["SiteAnalytics"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "SiteAnalytics", back_populates="site", lazy="selectin", cascade="all, delete-orphan"
    )

    # Spatial index for efficient geospatial queries
    __table_args__ = (
        Index("idx_sites_geometry", "geometry", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<Site id={self.id} name={self.name}>"
