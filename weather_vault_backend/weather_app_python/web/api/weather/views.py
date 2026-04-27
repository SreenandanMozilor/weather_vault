import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from weather_app_python.db.dependencies import get_db_session
from weather_app_python.services.auth import get_current_user
from weather_app_python.db.models.user_model import User
from weather_app_python.db.models.search_history_model import SearchHistory
from weather_app_python.db.dao.saved_weather_dao import SavedWeatherDAO
from weather_app_python.services.weather.client import WeatherClient
from weather_app_python.web.api.weather.schema import CityRequest, MessageResponse, DashboardResponse, HistoryResponse, CurrentWeatherResponse

router = APIRouter()
weather_client = WeatherClient()

@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    city_name: str,
    current_user: User = Depends(get_current_user)
) -> CurrentWeatherResponse:
    """Fetches live weather without saving it."""
    geo_data = await weather_client.get_coordinates(city_name)
    weather_data = await weather_client.get_weather_data(geo_data["latitude"], geo_data["longitude"])
    
    return CurrentWeatherResponse(
        city=city_name, 
        weather=weather_data
    )

@router.post("/save", response_model=MessageResponse)
async def save_city_weather(
    request: CityRequest,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
) -> MessageResponse:
    dao = SavedWeatherDAO(db)
    
    total_cities = await dao.count_user_cities(current_user.userid)
    if total_cities >= 8:
        raise HTTPException(status_code=400, detail="Dashboard full! You can only save up to 8 cities.")
        
    existing = await dao.get_saved_city(current_user.userid, request.city_name)
    if existing:
         raise HTTPException(status_code=400, detail="You have already saved this city.")

    geo_data = await weather_client.get_coordinates(request.city_name)
    
    await dao.add_city(
        user_id=current_user.userid,
        city_name=request.city_name,
        country=geo_data["country"],
        lat=geo_data["latitude"],
        lon=geo_data["longitude"]
    )
    
    return MessageResponse(message=f"Successfully saved {request.city_name}!", city_data=geo_data)

@router.delete("/cities/{city_id}", response_model=MessageResponse)
async def delete_saved_city(
    city_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
) -> MessageResponse:
    dao = SavedWeatherDAO(db)
    deleted = await dao.delete_city(current_user.userid, city_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="City not found.")
        
    return MessageResponse(message="Successfully deleted city.")

@router.get("/dashboard", response_model=DashboardResponse)
async def get_weather_dashboard(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
) -> DashboardResponse:
    dao = SavedWeatherDAO(db)
    saved_cities = await dao.get_all_user_cities(current_user.userid)
    
    if not saved_cities:
        return DashboardResponse(dashboard=[])

    semaphore = asyncio.Semaphore(3)

    async def fetch_city_weather(city):
        async with semaphore:
            try:
                weather_data = await weather_client.get_weather_data(city.latitude, city.longitude)
                return {
                    "city_id": city.id,
                    "city_name": city.city_name,
                    "country": city.country,
                    "current_weather": weather_data.get("current", {})
                }
            except Exception:
                return {"city_id": city.id, "city_name": city.city_name, "country": city.country, "current_weather": {}}

    tasks = [fetch_city_weather(city) for city in saved_cities]
    dashboard_data = await asyncio.gather(*tasks)
    return DashboardResponse(dashboard=dashboard_data)

@router.post("/history", response_model=MessageResponse)
async def add_search_history(
    request: CityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> MessageResponse:
    new_search = SearchHistory(user_id=current_user.userid, city_name=request.city_name)
    db.add(new_search)
    return MessageResponse(message="History saved")

@router.get("/history", response_model=HistoryResponse)
async def get_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> HistoryResponse:
    query = select(SearchHistory.city_name).where(
        SearchHistory.user_id == current_user.userid
    ).order_by(SearchHistory.searched_at.desc()).limit(20)
    
    result = await db.execute(query)
    cities = result.scalars().all()
    
    seen = set()
    history = [x for x in cities if not (x in seen or seen.add(x))]
    
    return HistoryResponse(history=history[:5])