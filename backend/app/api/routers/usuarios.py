from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_role
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.api.services.usuario_service import (
    crear_usuario,
    obtener_usuario_por_id,
    obtener_usuarios,
    actualizar_usuario,
    eliminar_usuario
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return crear_usuario(db, usuario)

@router.get("/", response_model=list[UsuarioResponse], dependencies=[Depends(require_role("admin"))])
def listar_usuarios(db: Session = Depends(get_db)):
    return obtener_usuarios(db)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario_router(usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    return actualizar_usuario(db, usuario_id, datos)

@router.delete("/{usuario_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_usuario_router(usuario_id: int, db: Session = Depends(get_db)):
    eliminar_usuario(db, usuario_id)
    return {"mensaje": "Usuario eliminado correctamente"}
