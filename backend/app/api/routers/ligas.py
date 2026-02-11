from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.liga import LigaCreate, LigaUpdate, LigaResponse
from app.api.services.liga_service import (
    crear_liga,
    obtener_ligas,
    obtener_liga_por_id,
    actualizar_liga,
    eliminar_liga
)

router = APIRouter(
    prefix="/ligas",
    tags=["Ligas"]
)

@router.post("/", response_model=LigaResponse, dependencies=[Depends(require_role("admin"))])
def crear_liga_router(liga: LigaCreate, db: Session = Depends(get_db)):
    return crear_liga(db, liga)

@router.get("/", response_model=list[LigaResponse])
def listar_ligas(db: Session = Depends(get_db)):
    return obtener_ligas(db)

@router.get("/{liga_id}", response_model=LigaResponse)
def obtener_liga_router(liga_id: int, db: Session = Depends(get_db)):
    liga = obtener_liga_por_id(db, liga_id)
    if not liga:
        raise HTTPException(404, "Liga no encontrada")
    return liga

@router.put("/{liga_id}", response_model=LigaResponse, dependencies=[Depends(require_role("admin"))])
def actualizar_liga_router(liga_id: int, datos: LigaUpdate, db: Session = Depends(get_db)):
    return actualizar_liga(db, liga_id, datos)

@router.delete("/{liga_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_liga_router(liga_id: int, db: Session = Depends(get_db)):
    eliminar_liga(db, liga_id)
    return {"mensaje": "Liga eliminada"}
