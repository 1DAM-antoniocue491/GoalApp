from sqlalchemy.orm import Session

from app.models.rol import Rol
from app.schemas.rol import RolCreate, RolUpdate

# ============================================================
# CRUD ROLES
# ============================================================

def crear_rol(db: Session, datos: RolCreate):
    # Verificar nombre único
    existente = db.query(Rol).filter(Rol.nombre == datos.nombre).first()
    if existente:
        raise ValueError("Ya existe un rol con ese nombre")

    rol = Rol(
        nombre=datos.nombre,
        descripcion=datos.descripcion
    )

    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


def obtener_roles(db: Session):
    return db.query(Rol).all()


def obtener_rol_por_id(db: Session, rol_id: int):
    return db.query(Rol).filter(Rol.id_rol == rol_id).first()


def actualizar_rol(db: Session, rol_id: int, datos: RolUpdate):
    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise ValueError("Rol no encontrado")

    if datos.nombre is not None:
        # Verificar nombre único
        existente = db.query(Rol).filter(
            Rol.nombre == datos.nombre,
            Rol.id_rol != rol_id
        ).first()
        if existente:
            raise ValueError("Ya existe otro rol con ese nombre")

        rol.nombre = datos.nombre

    if datos.descripcion is not None:
        rol.descripcion = datos.descripcion

    db.commit()
    db.refresh(rol)
    return rol


def eliminar_rol(db: Session, rol_id: int):
    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise ValueError("Rol no encontrado")

    db.delete(rol)
    db.commit()
