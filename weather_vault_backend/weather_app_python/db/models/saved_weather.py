from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Float
from weather_app_python.db.base import Base

class SavedWeather(Base):
    __tablename__ = "saved_weather"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user.userid")) #Foreign Key
    
    city_name: Mapped[str] = mapped_column(String(length=100))
    country: Mapped[str] = mapped_column(String(length=100))
    
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)