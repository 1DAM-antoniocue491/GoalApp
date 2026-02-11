from sqlalchemy.orm import Session
from app.models.liga import Liga
from app.schemas.liga import LigaCreate, LigaUpdate

def crear_liga(db: Session, datos: LigaCreate):
    liga = Liga(
        nombre=datos.nombre,
        temporada=datos.temporada
    )
    db.add(liga)
    db.commit()
    db.refresh(liga)
    return liga

def obtener_ligas(db: Session):
    return db.query(Liga).all()

def obtener_liga_por_id(db: Session, liga_id: int):
    return db.query(Liga).filter(Liga.id_liga == liga_id).first()

def actualizar_liga(db: Session, liga_id: int, datos: LigaUpdate):
    liga = obtener_liga_por_id(db, liga_id)
    if not liga:
        raise ValueError("Liga no encontrada")

    if datos.nombre is not None:
        liga.nombre = datos.nombre
    if datos.temporada is not None:
        liga.temporada = datos.temporada

    db.commit()
    db.refresh(liga)
    return liga

def eliminar_liga(db: Session, liga_id: int):
    liga = obtener_liga_por_id(db, liga_id)
    if not liga:
        raise ValueError("Liga no encontrada")

    db.delete(liga)
    db.commit()
