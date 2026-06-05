from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

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

    app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/ui")

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
