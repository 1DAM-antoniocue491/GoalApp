# app/api/routers/eventos.py
"""
Router de Eventos - Gestión de eventos de partido.
Endpoints para registrar y consultar eventos ocurridos durante los partidos
(goles, tarjetas, sustituciones, etc.).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.eventos import EventoPartidoBase, EventoPartidoCreate, EventoPartidoUpdate, EventoPartidoResponse
from app.api.services.evento_service import (
    crear_evento,
    obtener_eventos_por_partido
)
from app.models.evento_partido import EventoPartido

# Configuración del router
router = APIRouter(
    prefix="/eventos",  # Base path: /api/v1/eventos
    tags=["Eventos"]  # Agrupación en documentación
)

@router.post("/", response_model=EventoPartidoResponse, dependencies=[Depends(require_role("admin"))])
def crear_evento_router(evento: EventoPartidoCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo evento en un partido.
    
    Crea un evento durante el transcurso de un partido (gol, tarjeta amarilla,
    tarjeta roja, sustitución, etc.).
    
    Parámetros:
        - evento (EventoPartidoCreate): Datos del evento (partido_id, jugador_id, minuto, tipo)
        - db (Session): Sesión de base de datos
    
    Returns:
        EventoPartidoResponse: Información del evento creado
    
    Requiere autenticación: Sí
    Roles permitidos: Admin
    """
    return crear_evento(db, evento)

@router.get("/partido/{partido_id}", response_model=list[EventoPartidoResponse])
def listar_eventos_partido(partido_id: int, db: Session = Depends(get_db)):
    """
    Listar todos los eventos de un partido específico.
    
    Obtiene la cronología completa de eventos ocurridos durante un partido,
    ordenados por minuto de juego.
    
    Parámetros:
        - partido_id (int): ID del partido (path parameter)
        - db (Session): Sesión de base de datos
    
    Returns:
        List[EventoPartidoResponse]: Lista de eventos del partido
    
    Requiere autenticación: No
    Roles permitidos: Público
    """
    return obtener_eventos_por_partido(db, partido_id)
