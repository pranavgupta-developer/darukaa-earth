"""
SiteAnalytics SQLAlchemy model.

Stores time-series performance metrics for sites:
- NDVI (vegetation index)
- Carbon sequestration (tons)
- Biodiversity index
- Canopy cover percentage
- Extensible metadata JSON column
"""

import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class SiteAnalytics(UUIDMixin, TimestampMixin, Base):
    """Time-series analytics data for a site."""

    __tablename__ = "site_analytics"

    site_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    ndvi: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbon_sequestration_tons: Mapped[float | None] = mapped_column(Float, nullable=True)
    biodiversity_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    canopy_cover_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    site: Mapped["Site"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Site", back_populates="analytics"
    )

    __table_args__ = (
        Index("idx_site_analytics_site_date", "site_id", "recorded_date"),
    )

    def __repr__(self) -> str:
        return f"<SiteAnalytics site_id={self.site_id} date={self.recorded_date}>"
