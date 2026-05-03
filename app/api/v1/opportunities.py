from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_auth

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


# TODO(#10): Implementar endpoints de oportunidades en Sprint 6.
# GET /opportunities — lista paginada con filtros (status, categoría, margen)
# GET /opportunities/{id} — detalle
# POST /opportunities/{id}/dismiss — descartar
# POST /opportunities/{id}/evaluate — evaluar con IA (Sprint 7)
# POST /opportunities/{id}/publish — publicar en ML (Sprint 9)


@router.get("/", dependencies=[Depends(require_auth)])
async def list_opportunities() -> dict[str, str]:
    """Lista oportunidades detectadas. Implementar en Sprint 6."""
    return {"message": "Próximamente — Sprint 6"}
