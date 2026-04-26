from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import asyncio

# Import the Database Dependency
from weather_app_python.db.dependencies import get_db_session

# Import the Bouncer, the Vault, and the User Model
from weather_app_python.web.api.weather.saved_weather_create import SavedWeatherCreate
from weather_app_python.db.models.saved_weather import SavedWeather
from weather_app_python.db.models.user import User

# Import the Security Guard and the Weather Service
from weather_app_python.web.api.users.views import get_current_user
from weather_app_python.services.weather.client import WeatherClient

router = APIRouter()
weather_client = WeatherClient()

# Notice we only need the city name from the frontend now, not the coordinates!
from pydantic import BaseModel
class CityRequest(BaseModel):
    city_name: str

@router.post("/save")
async def save_city_weather(
    request: CityRequest,
    current_user: User = Depends(get_current_user), # The Security Guard is active!
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

    # 2. Get coordinates from Open-Meteo using our new service
    geo_data = await weather_client.get_coordinates(request.city_name)
    
    # 3. Create the Database Record (The Vault)
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
    
    # Optional: We could fetch the initial weather data here and return it, 
    # but returning the saved confirmation is usually enough.
    return {
        "message": f"Successfully saved {request.city_name}!",
        "city_data": geo_data
    }

@router.get("/cities")
async def get_saved_cities(
    current_user: User = Depends(get_current_user), # Security Guard is active!
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves all saved cities for the currently authenticated user."""
    
    # 1. Search the vault ONLY for cities belonging to this specific user
    query = select(SavedWeather).where(SavedWeather.user_id == current_user.userid)
    result = await db.execute(query)
    
    # 2. .all() grabs all matching rows as a list of Python objects
    saved_cities = result.scalars().all()
    
    # 3. Return them to the frontend
    return {"cities": saved_cities}

@router.delete("/cities/{city_id}")
async def delete_saved_city(
    city_id: int, # FastAPI automatically extracts this from the URL!
    current_user: User = Depends(get_current_user), # Security Guard
    db: AsyncSession = Depends(get_db_session)
):
    """Deletes a specific saved city for the logged-in user."""
    
    # 1. Find the exact city. 
    # CRITICAL SECURITY: We MUST check that the user_id matches the current_user!
    # Otherwise, a hacker could delete other people's cities by guessing IDs.
    query = select(SavedWeather).where(
        (SavedWeather.id == city_id) & 
        (SavedWeather.user_id == current_user.userid)
    )
    result = await db.execute(query)
    city_to_delete = result.scalars().first()
    
    # 2. If it doesn't exist (or belongs to someone else), throw a 404
    if not city_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found or you don't have permission to delete it."
        )
        
    # 3. Delete it from the Vault
    await db.delete(city_to_delete)
    await db.commit()
    
    return {"message": f"Successfully deleted {city_to_delete.city_name}."}

@router.get("/dashboard")
async def get_weather_dashboard(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session)
):
    """Fetches saved cities and their LIVE weather data concurrently."""
    
    # 1. Grab the user's saved cities from the Vault
    query = select(SavedWeather).where(SavedWeather.user_id == current_user.userid)
    result = await db.execute(query)
    saved_cities = result.scalars().all()
    
    # If they have no cities, return an empty array
    if not saved_cities:
        return {"dashboard": []}

    # 2. Define a mini-function to fetch weather for a single city
    async def fetch_city_weather(city: SavedWeather):
        try:
            # Hit our Service Desk (Open-Meteo) for the live data
            weather_data = await weather_client.get_weather_data(city.latitude, city.longitude)
            return {
                "city_id": city.id,
                "city_name": city.city_name,
                "country": city.country,
                "current_weather": weather_data.get("current", {})
            }
        except Exception:
            # If Open-Meteo fails for one city, don't crash the whole dashboard!
            return {
                "city_id": city.id,
                "city_name": city.city_name,
                "error": "Failed to load live weather."
            }

    # 3. Create a list of tasks for all cities
    tasks = [fetch_city_weather(city) for city in saved_cities]
    
    # 4. Fire them all at the exact same time!
    dashboard_data = await asyncio.gather(*tasks)
    
    # 5. Return the combined data to the frontend
    return {"dashboard": dashboard_data}