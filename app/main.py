from fastapi import FastAPI

from app.api.router import api_router
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.utils.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
