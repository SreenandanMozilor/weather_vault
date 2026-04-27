import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from weather_app_python.settings import settings

async def clear_data():
    # Connect using your app's existing configuration
    engine = create_async_engine(str(settings.db_url))
    
    async with engine.begin() as conn:
        print("Clearing existing data to prepare for enterprise schema...")
        # TRUNCATE removes all rows and CASCADE ensures child records are deleted
        await conn.execute(text("TRUNCATE TABLE \"user\", saved_weather, search_history CASCADE;"))
        
    print("✅ Database cleared. You are ready for the migration!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(clear_data())