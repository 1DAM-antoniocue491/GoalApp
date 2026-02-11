from sqlalchemy.orm import Session
from app.models.partido import Partido
from app.schemas.partido import PartidoCreate, PartidoUpdate

def crear_partido(db: Session, datos: PartidoCreate):
    partido = Partido(
        id_liga=datos.id_liga,
        id_equipo_local=datos.id_equipo_local,
        id_equipo_visitante=datos.id_equipo_visitante,
        fecha=datos.fecha,
        estado=datos.estado,
        goles_local=datos.goles_local,
        goles_visitante=datos.goles_visitante
    )
    db.add(partido)
    db.commit()
    db.refresh(partido)
    return partido

def obtener_partidos(db: Session):
    return db.query(Partido).all()

def obtener_partido_por_id(db: Session, partido_id: int):
    return db.query(Partido).filter(Partido.id_partido == partido_id).first()

def actualizar_partido(db: Session, partido_id: int, datos: PartidoUpdate):
    partido = obtener_partido_por_id(db, partido_id)
    if not partido:
        raise ValueError("Partido no encontrado")

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(partido, campo, valor)

    db.commit()
    db.refresh(partido)
    return partido

def eliminar_partido(db: Session, partido_id: int):
    partido = obtener_partido_por_id(db, partido_id)
    if not partido:
        raise ValueError("Partido no encontrado")

    db.delete(partido)
    db.commit()
