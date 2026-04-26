from pydantic import BaseModel, Field

class SavedWeatherCreate(BaseModel):
    # Temporary: Until we build JWT login tokens, we will just pass the user_id manually
    user_id: int 
    
    city_name: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    
    # Mathematical boundaries for planet Earth!
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)