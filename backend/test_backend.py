import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.config import settings
from app.models.user import User
from app.models.project import Project, ProjectType
from app.models.site import Site
from app.models.site_analytics import SiteAnalytics
from app.services.analytics_service import AnalyticsService

async def main():
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Get a user
        result = await db.execute("SELECT id FROM users LIMIT 1")
        user_row = result.first()
        if not user_row:
            print("No users found")
            return
        
        user_id = user_row[0]
        user = User(id=user_id)
        
        service = AnalyticsService(db)
        try:
            res = await service.get_global_analytics(user=user)
            print("SUCCESS:")
            print(res.json())
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(main())
