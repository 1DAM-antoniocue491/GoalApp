from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.evento import EventoCreate, EventoResponse
from app.api.services.evento_service import (
    crear_evento,
    obtener_eventos_por_partido
)

router = APIRouter(
    prefix="/eventos",
    tags=["Eventos"]
)

@router.post("/", response_model=EventoResponse, dependencies=[Depends(require_role("admin"))])
def crear_evento_router(evento: EventoCreate, db: Session = Depends(get_db)):
    return crear_evento(db, evento)

@router.get("/partido/{partido_id}", response_model=list[EventoResponse])
def listar_eventos_partido(partido_id: int, db: Session = Depends(get_db)):
    return obtener_eventos_por_partido(db, partido_id)
