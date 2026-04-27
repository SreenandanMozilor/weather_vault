from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CityRequest(BaseModel):
    """Schema for incoming city requests (Priority Fix #10)."""
    city_name: str

class MessageResponse(BaseModel):
    message: str
    city_data: Optional[Dict[str, Any]] = None

class DashboardCity(BaseModel):
    city_id: int
    city_name: str
    country: str
    current_weather: Dict[str, Any]

class DashboardResponse(BaseModel):
    dashboard: List[DashboardCity]

class HistoryResponse(BaseModel):
    history: List[str]

class CurrentWeatherResponse(BaseModel):
    city: str
    weather: Dict[str, Any]