from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_auth

router = APIRouter(prefix="/publications", tags=["publications"])


# TODO(#12): Implementar endpoints de publicaciones en Sprint 9.
# GET /publications — lista de publicaciones activas en ML
# GET /publications/{id} — detalle con estado actual en ML
# PUT /publications/{id}/pause — pausar publicación
# PUT /publications/{id}/close — cerrar publicación


@router.get("/", dependencies=[Depends(require_auth)])
async def list_publications() -> dict[str, str]:
    """Lista publicaciones en Mercado Libre. Implementar en Sprint 9."""
    return {"message": "Próximamente — Sprint 9"}
