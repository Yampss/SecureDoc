from fastapi import Depends, HTTPException, Request, status

from app.auth.models import UserContext
from app.config.settings import Settings, get_settings


def get_current_user(
    request: Request, settings: Settings = Depends(get_settings)
) -> UserContext:
    user_id = request.headers.get(settings.cognito_username_header)
    role = request.headers.get(settings.cognito_role_header)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: missing Cognito identity header.",
        )

    return UserContext(user_id=user_id, role=role)
