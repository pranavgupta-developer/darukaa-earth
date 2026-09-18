"""
Seed script: Generate realistic mock analytics time-series data.

Generates 24 months of monthly data for all existing sites with
realistic seasonal patterns and noise for:
- NDVI (0.2–0.9, seasonal variation)
- Carbon sequestration (0.5–5.0 tons/month, growing trend)
- Biodiversity index (0.3–0.8, stable with noise)
- Canopy cover (30–85%, slow growth)

Usage:
    cd backend
    python -m scripts.seed_analytics
"""

import asyncio
import math
import random
import uuid
from datetime import date, timedelta

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
import app.models  # Ensures all models are imported and registered
from app.models.project import Project
from app.models.site import Site
from app.models.site_analytics import SiteAnalytics


async def seed_analytics() -> None:
    """Generate mock analytics data for all existing sites."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Site.id, Site.name))
        sites = result.all()

        if not sites:
            print("No sites found. Create projects and sites first.")
            return

        records: list[SiteAnalytics] = []
        today = date.today()
        start = today - timedelta(days=730)  # ~24 months ago

        for site_id, site_name in sites:
            print(f"Generating data for site: {site_name} ({site_id})")
            current = start

            # Base values with per-site randomization
            base_ndvi = random.uniform(0.35, 0.55)
            base_carbon = random.uniform(1.0, 2.5)
            base_biodiversity = random.uniform(0.4, 0.6)
            base_canopy = random.uniform(40, 55)

            month_idx = 0
            while current <= today:
                # Seasonal NDVI pattern (peaks in summer/monsoon)
                seasonal = math.sin(2 * math.pi * (current.month - 3) / 12)
                ndvi = base_ndvi + 0.2 * seasonal + random.gauss(0, 0.03)
                ndvi = max(0.1, min(0.95, ndvi))

                # Carbon sequestration with upward trend
                carbon = base_carbon + 0.05 * month_idx + random.gauss(0, 0.2)
                carbon = max(0.1, carbon)

                # Biodiversity index — relatively stable
                biodiversity = base_biodiversity + random.gauss(0, 0.02)
                biodiversity = max(0.1, min(1.0, biodiversity))

                # Canopy cover — slow growth
                canopy = base_canopy + 0.3 * month_idx + random.gauss(0, 1.5)
                canopy = max(10, min(95, canopy))

                records.append(
                    SiteAnalytics(
                        site_id=site_id,
                        recorded_date=current,
                        ndvi=round(ndvi, 4),
                        carbon_sequestration_tons=round(carbon, 2),
                        biodiversity_index=round(biodiversity, 4),
                        canopy_cover_pct=round(canopy, 1),
                    )
                )

                # Advance ~1 month
                current += timedelta(days=30)
                month_idx += 1

        db.add_all(records)
        await db.commit()
        print(f"Seeded {len(records)} analytics records for {len(sites)} sites.")


if __name__ == "__main__":
    asyncio.run(seed_analytics())
