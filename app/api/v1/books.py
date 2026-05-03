from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_auth

router = APIRouter(prefix="/books", tags=["books"])


# TODO(#11): Implementar endpoints de libros en Sprint 1/3.
# GET /books/{isbn} — detalle de libro por ISBN-13
# POST /books/search — buscar metadata por ISBN o título


@router.get("/", dependencies=[Depends(require_auth)])
async def list_books() -> dict[str, str]:
    """Lista libros en el catálogo. Implementar en Sprint 3."""
    return {"message": "Próximamente — Sprint 3"}
