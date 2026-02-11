from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.equipo import EquipoCreate, EquipoUpdate, EquipoResponse
from app.api.services.equipo_service import (
    crear_equipo,
    obtener_equipos,
    obtener_equipo_por_id,
    actualizar_equipo,
    eliminar_equipo
)

router = APIRouter(
    prefix="/equipos",
    tags=["Equipos"]
)

@router.post("/", response_model=EquipoResponse, dependencies=[Depends(require_role("admin"))])
def crear_equipo_router(equipo: EquipoCreate, db: Session = Depends(get_db)):
    return crear_equipo(db, equipo)

@router.get("/", response_model=list[EquipoResponse])
def listar_equipos(db: Session = Depends(get_db)):
    return obtener_equipos(db)

@router.get("/{equipo_id}", response_model=EquipoResponse)
def obtener_equipo_router(equipo_id: int, db: Session = Depends(get_db)):
    equipo = obtener_equipo_por_id(db, equipo_id)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    return equipo

@router.put("/{equipo_id}", response_model=EquipoResponse, dependencies=[Depends(require_role("admin"))])
def actualizar_equipo_router(equipo_id: int, datos: EquipoUpdate, db: Session = Depends(get_db)):
    return actualizar_equipo(db, equipo_id, datos)

@router.delete("/{equipo_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_equipo_router(equipo_id: int, db: Session = Depends(get_db)):
    eliminar_equipo(db, equipo_id)
    return {"mensaje": "Equipo eliminado correctamente"}
