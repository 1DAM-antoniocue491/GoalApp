"""
Servicios de lógica de negocio para Liga.
Maneja operaciones CRUD de ligas/competiciones, incluyendo gestión de
nombres y temporadas.
"""
from sqlalchemy.orm import Session
from app.models.liga import Liga
from app.schemas.liga import LigaCreate, LigaUpdate


def crear_liga(db: Session, datos: LigaCreate):
    """
    Crea una nueva liga en la base de datos.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        datos (LigaCreate): Datos de la liga (nombre y temporada)
    
    Returns:
        Liga: Objeto Liga creado con su ID asignado
    """
    liga = Liga(
        nombre=datos.nombre,
        temporada=datos.temporada
    )
    db.add(liga)
    db.commit()
    db.refresh(liga)
    return liga


def obtener_ligas(db: Session):
    """
    Obtiene todas las ligas registradas.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
    
    Returns:
        list[Liga]: Lista con todas las ligas
    """
    return db.query(Liga).all()


def obtener_liga_por_id(db: Session, liga_id: int):
    """
    Busca una liga por su ID.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        liga_id (int): ID de la liga a buscar
    
    Returns:
        Liga: Objeto Liga si existe, None si no se encuentra
    """
    return db.query(Liga).filter(Liga.id_liga == liga_id).first()


def actualizar_liga(db: Session, liga_id: int, datos: LigaUpdate):
    """
    Actualiza los datos de una liga existente.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        liga_id (int): ID de la liga a actualizar
        datos (LigaUpdate): Datos a actualizar (nombre y/o temporada)
    
    Returns:
        Liga: Objeto Liga actualizado
    
    Raises:
        ValueError: Si la liga no existe
    """
    liga = obtener_liga_por_id(db, liga_id)
    if not liga:
        raise ValueError("Liga no encontrada")

    # Actualizar nombre si se proporciona
    if datos.nombre is not None:
        liga.nombre = datos.nombre
    # Actualizar temporada si se proporciona
    if datos.temporada is not None:
        liga.temporada = datos.temporada

    db.commit()
    db.refresh(liga)
    return liga


def eliminar_liga(db: Session, liga_id: int):
    """
    Elimina una liga de la base de datos.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        liga_id (int): ID de la liga a eliminar
    
    Raises:
        ValueError: Si la liga no existe
    """
    liga = obtener_liga_por_id(db, liga_id)
    if not liga:
        raise ValueError("Liga no encontrada")

    db.delete(liga)
    db.commit()
