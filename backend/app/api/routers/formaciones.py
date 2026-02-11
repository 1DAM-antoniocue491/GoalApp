from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.formacion import (
    FormacionCreate, FormacionResponse,
    PosicionCreate, PosicionResponse
)
from app.api.services.formacion_service import (
    crear_formacion,
    obtener_formaciones,
    crear_posicion,
    obtener_posiciones
)

router = APIRouter(
    prefix="/formaciones",
    tags=["Formaciones"]
)

@router.post("/", response_model=FormacionResponse, dependencies=[Depends(require_role("admin"))])
def crear_formacion_router(formacion: FormacionCreate, db: Session = Depends(get_db)):
    return crear_formacion(db, formacion)

@router.get("/", response_model=list[FormacionResponse])
def listar_formaciones(db: Session = Depends(get_db)):
    return obtener_formaciones(db)

@router.post("/posiciones", response_model=PosicionResponse, dependencies=[Depends(require_role("admin"))])
def crear_posicion_router(posicion: PosicionCreate, db: Session = Depends(get_db)):
    return crear_posicion(db, posicion)

@router.get("/posiciones/{formacion_id}", response_model=list[PosicionResponse])
def listar_posiciones(formacion_id: int, db: Session = Depends(get_db)):
    return obtener_posiciones(db, formacion_id)
