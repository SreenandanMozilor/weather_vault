from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from sqlalchemy.sql import func

from weather_app_python.db.base import Base

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Link every search exactly to the user who searched it
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.userid", ondelete="CASCADE"))
    city_name: Mapped[str] = mapped_column(String(200))
    # Review Fix #14: Ensure the timestamp is present for tracking
    searched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())