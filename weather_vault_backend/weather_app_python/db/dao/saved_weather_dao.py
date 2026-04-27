from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from weather_app_python.db.models.saved_weather_model import SavedWeather

class SavedWeatherDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_saved_city(self, user_id: int, city_name: str) -> SavedWeather | None:
        query = select(SavedWeather).where(
            (SavedWeather.user_id == user_id) & 
            (SavedWeather.city_name.ilike(city_name))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def count_user_cities(self, user_id: int) -> int:
        query = select(func.count()).select_from(SavedWeather).where(
            SavedWeather.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def add_city(self, user_id: int, city_name: str, country: str, lat: float, lon: float) -> SavedWeather:
        new_city = SavedWeather(
            user_id=user_id, city_name=city_name, country=country, latitude=lat, longitude=lon
        )
        self.session.add(new_city)
        await self.session.flush()
        return new_city

    async def get_all_user_cities(self, user_id: int) -> list[SavedWeather]:
        query = select(SavedWeather).where(SavedWeather.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_city(self, user_id: int, city_id: int) -> SavedWeather | None:
        query = select(SavedWeather).where(
            (SavedWeather.id == city_id) & (SavedWeather.user_id == user_id)
        )
        result = await self.session.execute(query)
        city_to_delete = result.scalars().first()
        
        if city_to_delete:
            await self.session.delete(city_to_delete)
            await self.session.flush()
        return city_to_delete