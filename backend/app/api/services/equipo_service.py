from sqlalchemy.orm import Session
from app.models.equipo import Equipo
from app.schemas.equipo import EquipoCreate, EquipoUpdate

def crear_equipo(db: Session, datos: EquipoCreate):
    equipo = Equipo(
        nombre=datos.nombre,
        escudo=datos.escudo,
        colores=datos.colores,
        id_liga=datos.id_liga,
        id_entrenador=datos.id_entrenador,
        id_delegado=datos.id_delegado
    )
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo

def obtener_equipos(db: Session):
    return db.query(Equipo).all()

def obtener_equipo_por_id(db: Session, equipo_id: int):
    return db.query(Equipo).filter(Equipo.id_equipo == equipo_id).first()

def actualizar_equipo(db: Session, equipo_id: int, datos: EquipoUpdate):
    equipo = obtener_equipo_por_id(db, equipo_id)
    if not equipo:
        raise ValueError("Equipo no encontrado")

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)
    return equipo

def eliminar_equipo(db: Session, equipo_id: int):
    equipo = obtener_equipo_por_id(db, equipo_id)
    if not equipo:
        raise ValueError("Equipo no encontrado")

    db.delete(equipo)
    db.commit()
