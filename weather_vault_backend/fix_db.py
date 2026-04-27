import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from weather_app_python.settings import settings

async def fix_alembic():
    # 1. Connect to the database using your exact app settings
    engine = create_async_engine(str(settings.db_url))
    
    # 2. Perform the surgery
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE alembic_version SET version_num='7f67c0f9ec06';"))
        
    print("Database Surgery Successful! Alembic tracker restored.")
    
    # 3. Close connection cleanly
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_alembic())