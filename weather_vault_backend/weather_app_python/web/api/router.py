from fastapi.routing import APIRouter
from weather_app_python.web.api.docs import views as docs_views
from weather_app_python.web.api.monitoring import views as monitoring_views
from weather_app_python.web.api.users import views as users_views
from weather_app_python.web.api.weather import views as weather_views

api_router = APIRouter()

# Include the default monitoring/health-check router
api_router.include_router(monitoring_views.router)

# Include our custom enterprise routers
api_router.include_router(users_views.router, prefix="/users", tags=["users"])
api_router.include_router(weather_views.router, prefix="/weather", tags=["weather"])
api_router.include_router(docs_views.router)