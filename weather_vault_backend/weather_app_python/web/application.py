from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from weather_app_python.log import configure_logging
from weather_app_python.web.api.router import api_router
from weather_app_python.web.lifespan import lifespan_setup

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="weather_app_python",
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5500", "http://127.0.0.1:5500"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=api_router, prefix="/api")
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app
