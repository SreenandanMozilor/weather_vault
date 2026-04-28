from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from weather_app_python.db.models.search_history_model import SearchHistory

class SearchHistoryDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_search_history(self, user_id: int, city_name: str) -> SearchHistory:
        new_search = SearchHistory(user_id=user_id, city_name=city_name)
        self.session.add(new_search)
        await self.session.flush()
        return new_search

    async def get_recent_history(self, user_id: int, limit: int = 20) -> list[str]:
        query = select(SearchHistory.city_name).where(
            SearchHistory.user_id == user_id
        ).order_by(SearchHistory.searched_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        cities = result.scalars().all()
        
        seen = set()
        history = [x for x in cities if not (x in seen or seen.add(x))]
        return history[:5]