from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.jugador import JugadorCreate, JugadorUpdate, JugadorResponse
from app.api.services.jugador_service import (
    crear_jugador,
    obtener_jugadores,
    obtener_jugador_por_id,
    actualizar_jugador,
    eliminar_jugador
)

router = APIRouter(
    prefix="/jugadores",
    tags=["Jugadores"]
)

@router.post("/", response_model=JugadorResponse, dependencies=[Depends(require_role("admin"))])
def crear_jugador_router(jugador: JugadorCreate, db: Session = Depends(get_db)):
    return crear_jugador(db, jugador)

@router.get("/", response_model=list[JugadorResponse])
def listar_jugadores(db: Session = Depends(get_db)):
    return obtener_jugadores(db)

@router.get("/{jugador_id}", response_model=JugadorResponse)
def obtener_jugador_router(jugador_id: int, db: Session = Depends(get_db)):
    jugador = obtener_jugador_por_id(db, jugador_id)
    if not jugador:
        raise HTTPException(404, "Jugador no encontrado")
    return jugador

@router.put("/{jugador_id}", response_model=JugadorResponse, dependencies=[Depends(require_role("admin"))])
def actualizar_jugador_router(jugador_id: int, datos: JugadorUpdate, db: Session = Depends(get_db)):
    return actualizar_jugador(db, jugador_id, datos)

@router.delete("/{jugador_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_jugador_router(jugador_id: int, db: Session = Depends(get_db)):
    eliminar_jugador(db, jugador_id)
    return {"mensaje": "Jugador eliminado correctamente"}
