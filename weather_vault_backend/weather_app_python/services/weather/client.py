import httpx
import logging
import asyncio
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

shared_client = httpx.AsyncClient(
    timeout=httpx.Timeout(15.0),
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
)

class WeatherClient:
    def __init__(self):
        self.BASE_URL = "https://api.open-meteo.com/v1/forecast"
        self.GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

    async def get_coordinates(self, city_name: str) -> dict:
        """Fetches latitude and longitude for a given city name."""
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        try:
            response = await shared_client.get(self.GEO_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"City '{city_name}' not found."
                )
                
            city_data = data["results"][0]
            return {
                "latitude": city_data["latitude"],
                "longitude": city_data["longitude"],
                "country": city_data.get("country", "Unknown")
            }
        except httpx.HTTPError as e:
            logger.error("GEOCODING API ERROR: %s", repr(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch city coordinates."
            )

    async def get_weather_data(self, latitude: float, longitude: float) -> dict:
        """Fetches current and daily weather data using coordinates."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
        
        for attempt in range(3):
            try:

                response = await shared_client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
                
            except httpx.ConnectTimeout as e:
                if attempt == 2:
                    logger.error("OPEN-METEO CONNECTION ERROR: %s", repr(e))
                    raise HTTPException(status_code=502, detail="Failed to connect to Weather API")
                logger.warning(f"Connection timeout, retrying attempt {attempt + 1}...")
                await asyncio.sleep(0.5)
                
            except httpx.HTTPStatusError as e:
                logger.error("OPEN-METEO API ERROR: %s - %s", e.response.status_code, e.response.text)
                raise HTTPException(status_code=502, detail="Weather API error")
                
            except Exception as e:
                logger.error("OPEN-METEO UNKNOWN ERROR: %s", repr(e))
                raise HTTPException(status_code=502, detail="Failed to connect to Weather API")