from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime
from sqlalchemy.sql import func
from weather_app_python.db.base import Base

class SavedWeather(Base):
    __tablename__ = "saved_weather"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.userid", ondelete="CASCADE"))
    city_name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())