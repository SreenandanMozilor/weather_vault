from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import asyncio
from pydantic import BaseModel

# Import the Database Dependency
from weather_app_python.db.dependencies import get_db_session

# Import the Bouncer, the Vault, and the Models
from weather_app_python.web.api.weather.saved_weather_create import SavedWeatherCreate
from weather_app_python.db.models.saved_weather import SavedWeather
from weather_app_python.db.models.user import User
from weather_app_python.db.models.search_history import SearchHistory 

# Import the Security Guard and the Weather Service
from weather_app_python.web.api.users.views import get_current_user
from weather_app_python.services.weather.client import WeatherClient

router = APIRouter()
weather_client = WeatherClient()

class CityRequest(BaseModel):
    city_name: str

@router.post("/save")
async def save_city_weather(
    request: CityRequest,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """Saves a city for the currently authenticated user."""
    
    # 1. Check if the user already saved this city (prevent duplicates)
    query = select(SavedWeather).where(
        (SavedWeather.user_id == current_user.userid) & 
        (SavedWeather.city_name.ilike(request.city_name))
    )
    result = await db.execute(query)
    existing_city = result.scalars().first()
    
    if existing_city:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already saved this city."
        )
    
    # Enforces 8-city limit per user
    count_query = select(func.count()).select_from(SavedWeather).where(
        SavedWeather.user_id == current_user.userid
    )
    count_result = await db.execute(count_query)
    total_cities = count_result.scalar()
    
    if total_cities >= 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dashboard full! You can only save up to 8 cities."
        )

    # 2. Get coordinates from Open-Meteo
    geo_data = await weather_client.get_coordinates(request.city_name)
    
    # 3. Create the Database Record 
    new_saved_city = SavedWeather(
        user_id=current_user.userid,
        city_name=request.city_name,
        country=geo_data["country"],
        latitude=geo_data["latitude"],
        longitude=geo_data["longitude"]
    )
    
    # 4. Save to PostgreSQL
    db.add(new_saved_city)
    await db.commit()
    
    return {
        "message": f"Successfully saved {request.city_name}!",
        "city_data": geo_data
    }

@router.get("/cities")
async def get_saved_cities(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves all saved cities for the currently authenticated user."""
    query = select(SavedWeather).where(SavedWeather.user_id == current_user.userid)
    result = await db.execute(query)
    saved_cities = result.scalars().all()
    return {"cities": saved_cities}

@router.delete("/cities/{city_id}")
async def delete_saved_city(
    city_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """Deletes a specific saved city for the logged-in user."""
    query = select(SavedWeather).where(
        (SavedWeather.id == city_id) & 
        (SavedWeather.user_id == current_user.userid)
    )
    result = await db.execute(query)
    city_to_delete = result.scalars().first()
    
    if not city_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found or you don't have permission to delete it."
        )
        
    await db.delete(city_to_delete)
    await db.commit()
    
    return {"message": f"Successfully deleted {city_to_delete.city_name}."}

@router.get("/dashboard")
async def get_weather_dashboard(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """Fetches saved cities and their LIVE weather data concurrently."""
    query = select(SavedWeather).where(SavedWeather.user_id == current_user.userid)
    result = await db.execute(query)
    saved_cities = result.scalars().all()
    
    if not saved_cities:
        return {"dashboard": []}

    async def fetch_city_weather(city: SavedWeather):
        try:
            weather_data = await weather_client.get_weather_data(city.latitude, city.longitude)
            return {
                "city_id": city.id,
                "city_name": city.city_name,
                "country": city.country,
                "current_weather": weather_data.get("current", {})
            }
        except Exception:
            return {
                "city_id": city.id,
                "city_name": city.city_name,
                "error": "Failed to load live weather."
            }

    tasks = [fetch_city_weather(city) for city in saved_cities]
    dashboard_data = await asyncio.gather(*tasks)
    return {"dashboard": dashboard_data}

# Search History Endpoints

@router.post("/history")
async def add_search_history(
    request: CityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Saves a new search query to the database."""
    new_search = SearchHistory(user_id=current_user.userid, city_name=request.city_name)
    db.add(new_search)
    await db.commit()
    return {"message": "History saved"}

@router.get("/history")
async def get_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves the user's 5 most recent unique searches."""
    query = select(SearchHistory.city_name).where(
        SearchHistory.user_id == current_user.userid
    ).order_by(SearchHistory.searched_at.desc()).limit(20)
    
    result = await db.execute(query)
    cities = result.scalars().all()
    
    # Deduplicate the list while preserving the most recent order
    seen = set()
    history = [x for x in cities if not (x in seen or seen.add(x))]
    
    return {"history": history[:5]}