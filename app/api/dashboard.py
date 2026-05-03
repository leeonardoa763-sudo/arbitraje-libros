from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_auth

router = APIRouter(tags=["dashboard"])


@router.get("/", dependencies=[Depends(require_auth)])
async def dashboard_home() -> dict[str, str]:
    """Dashboard principal de oportunidades.

    Implementar en Sprint 6 con Jinja2 + HTMX + Tailwind.
    """
    return {"message": "Dashboard en construcción — Sprint 6"}
