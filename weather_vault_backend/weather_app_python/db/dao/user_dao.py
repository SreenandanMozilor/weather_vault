from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from weather_app_python.db.models.user_model import User

class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_identifier(self, identifier: str) -> User | None:
        query = select(User).where(or_(User.username == identifier, User.email == identifier))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def check_user_exists(self, username: str, email: str) -> dict:
        query = select(User).where(or_(User.username == username, User.email == email))
        result = await self.session.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            return {"exists": False}
        if existing_user.email == email:
            return {"exists": True, "field": "email"}
        return {"exists": True, "field": "username"}

    async def create_user_model(self, email: str, username: str, hashed_password: str) -> User:
        new_user = User(email=email, username=username, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.flush()
        return new_user