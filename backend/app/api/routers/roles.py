from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.rol import RolCreate, RolUpdate, RolResponse
from app.api.services.rol_service import (
    crear_rol,
    obtener_roles,
    actualizar_rol,
    eliminar_rol,
    asignar_rol_a_usuario
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.post("/", response_model=RolResponse, dependencies=[Depends(require_role("admin"))])
def crear_rol_router(rol: RolCreate, db: Session = Depends(get_db)):
    return crear_rol(db, rol)

@router.get("/", response_model=list[RolResponse])
def listar_roles(db: Session = Depends(get_db)):
    return obtener_roles(db)

@router.put("/{rol_id}", response_model=RolResponse, dependencies=[Depends(require_role("admin"))])
def actualizar_rol_router(rol_id: int, datos: RolUpdate, db: Session = Depends(get_db)):
    return actualizar_rol(db, rol_id, datos)

@router.delete("/{rol_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_rol_router(rol_id: int, db: Session = Depends(get_db)):
    eliminar_rol(db, rol_id)
    return {"mensaje": "Rol eliminado"}

@router.post("/asignar/{usuario_id}/{rol_id}", dependencies=[Depends(require_role("admin"))])
def asignar_rol(usuario_id: int, rol_id: int, db: Session = Depends(get_db)):
    asignar_rol_a_usuario(db, usuario_id, rol_id)
    return {"mensaje": "Rol asignado correctamente"}
