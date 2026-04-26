import httpx
from fastapi import HTTPException, status

class WeatherClient:
    """Service class to handle external Open-Meteo API calls."""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    async def get_coordinates(self, city_name: str) -> dict:
        """Translates a city name into latitude and longitude."""
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.GEOCODING_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("results"):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"City '{city_name}' not found."
                    )
                
                # Extract the first result
                result = data["results"][0]
                return {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "country": result.get("country", "Unknown")
                }
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to communicate with Geocoding API: {str(e)}"
                )

    async def get_weather_data(self, latitude: float, longitude: float) -> dict:
            """Fetches current and daily weather data using coordinates."""
            params = {
                "latitude": latitude,
                "longitude": longitude,
                # Open-Meteo requires comma-separated strings, not Python lists
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "timezone": "auto"
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(self.BASE_URL, params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as e:
                    print(f"OPEN-METEO ERROR: {str(e)}") 
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Failed to fetch weather data: {str(e)}"
                    )