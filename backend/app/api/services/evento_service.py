from sqlalchemy.orm import Session
from app.models.evento_partido import EventoPartido
from app.schemas.evento import EventoCreate

def crear_evento(db: Session, datos: EventoCreate):
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
    return db.query(EventoPartido).filter(EventoPartido.id_partido == partido_id).all()
