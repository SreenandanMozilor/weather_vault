import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from weather_app_python.settings import settings

async def drop_all_tables():
    engine = create_async_engine(str(settings.db_url))
    
    async with engine.begin() as conn:
        print("Dropping all existing tables to prepare for a clean migration...")
        # Drop your app tables
        await conn.execute(text("DROP TABLE IF EXISTS search_history CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS saved_weather CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS \"user\" CASCADE;"))
        # Drop the alembic tracking table
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        
    print(" Database is now completely empty!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(drop_all_tables())