from fastapi.routing import APIRouter
from weather_app_python.web.api import docs, monitoring
from weather_app_python.web.api.users import views as users_views
from weather_app_python.web.api.weather import views as weather_views

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(users_views.router, prefix="/users", tags=["users"])
api_router.include_router(weather_views.router, prefix="/weather", tags=["weather"])