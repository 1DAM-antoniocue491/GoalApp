from sqlalchemy.orm import Session
from app.models.jugador import Jugador
from app.schemas.jugador import JugadorCreate, JugadorUpdate

def crear_jugador(db: Session, datos: JugadorCreate):
    jugador = Jugador(
        id_usuario=datos.id_usuario,
        id_equipo=datos.id_equipo,
        posicion=datos.posicion,
        dorsal=datos.dorsal,
        activo=datos.activo
    )
    db.add(jugador)
    db.commit()
    db.refresh(jugador)
    return jugador

def obtener_jugadores(db: Session):
    return db.query(Jugador).all()

def obtener_jugador_por_id(db: Session, jugador_id: int):
    return db.query(Jugador).filter(Jugador.id_jugador == jugador_id).first()

def actualizar_jugador(db: Session, jugador_id: int, datos: JugadorUpdate):
    jugador = obtener_jugador_por_id(db, jugador_id)
    if not jugador:
        raise ValueError("Jugador no encontrado")

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(jugador, campo, valor)

    db.commit()
    db.refresh(jugador)
    return jugador

def eliminar_jugador(db: Session, jugador_id: int):
    jugador = obtener_jugador_por_id(db, jugador_id)
    if not jugador:
        raise ValueError("Jugador no encontrado")

    db.delete(jugador)
    db.commit()
