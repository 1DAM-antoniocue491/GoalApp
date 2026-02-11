from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.partido import PartidoCreate, PartidoUpdate, PartidoResponse
from app.api.services.partido_service import (
    crear_partido,
    obtener_partidos,
    obtener_partido_por_id,
    actualizar_partido,
    eliminar_partido
)

router = APIRouter(
    prefix="/partidos",
    tags=["Partidos"]
)

@router.post("/", response_model=PartidoResponse, dependencies=[Depends(require_role("admin"))])
def crear_partido_router(partido: PartidoCreate, db: Session = Depends(get_db)):
    return crear_partido(db, partido)

@router.get("/", response_model=list[PartidoResponse])
def listar_partidos(db: Session = Depends(get_db)):
    return obtener_partidos(db)

@router.get("/{partido_id}", response_model=PartidoResponse)
def obtener_partido_router(partido_id: int, db: Session = Depends(get_db)):
    partido = obtener_partido_por_id(db, partido_id)
    if not partido:
        raise HTTPException(404, "Partido no encontrado")
    return partido

@router.put("/{partido_id}", response_model=PartidoResponse, dependencies=[Depends(require_role("admin"))])
def actualizar_partido_router(partido_id: int, datos: PartidoUpdate, db: Session = Depends(get_db)):
    return actualizar_partido(db, partido_id, datos)

@router.delete("/{partido_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_partido_router(partido_id: int, db: Session = Depends(get_db)):
    eliminar_partido(db, partido_id)
    return {"mensaje": "Partido eliminado correctamente"}
