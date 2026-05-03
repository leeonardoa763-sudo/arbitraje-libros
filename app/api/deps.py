from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import get_settings
from app.core.auth import verify_credentials
from app.database import get_db as get_db  # re-export para uso en routers

__all__ = ["get_db", "require_auth", "security"]

security = HTTPBasic()


async def require_auth(
    credentials: HTTPBasicCredentials = Depends(security),
) -> None:
    """Dependencia FastAPI que exige HTTP Basic Auth.

    Raises:
        HTTPException 401: si las credenciales son incorrectas o no se envían.
    """
    settings = get_settings()
    if not verify_credentials(
        credentials,
        expected_username=settings.app_username,
        expected_password=settings.app_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
