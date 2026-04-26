from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from weather_app_python.db.base import Base


class User(Base):
    """Model for demo purpose."""

    __tablename__ = "user"

    userid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(length=200))
    hashed_password: Mapped[str] = mapped_column(String(length = 256))