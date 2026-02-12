"""
Servicios de lógica de negocio para EventoPartido.
Maneja la gestión de eventos de partido (goles, tarjetas, sustituciones, etc.)
y su registro en la base de datos.
"""
from sqlalchemy.orm import Session
from app.models.evento_partido import EventoPartido
from app.schemas.eventos import EventoPartidoCreate


def crear_evento(db: Session, datos: EventoPartidoCreate):
    """
    Registra un nuevo evento en un partido.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        datos (EventoPartidoCreate): Datos del evento (partido, jugador, tipo, minuto)
    
    Returns:
        EventoPartido: Objeto EventoPartido creado con su ID asignado
    """
    evento = EventoPartido(
        id_partido=datos.id_partido,
        id_jugador=datos.id_jugador,
        tipo_evento=datos.tipo_evento,
        minuto=datos.minuto
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def obtener_eventos_por_partido(db: Session, partido_id: int):
    """
    Obtiene todos los eventos de un partido específico.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        partido_id (int): ID del partido
    
    Returns:
        list[EventoPartido]: Lista de eventos ordenados cronológicamente
    """
    return db.query(EventoPartido).filter(EventoPartido.id_partido == partido_id).order_by(EventoPartido.minuto).all()
