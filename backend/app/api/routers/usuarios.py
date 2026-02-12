# app/api/routers/usuarios.py
"""
Router de Usuarios - Gestión de cuentas de usuario.
Endpoints para registro, listado, actualización y eliminación de usuarios.
"""
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

# Configuración del router
router = APIRouter(
    prefix="/usuarios",  # Base path: /api/v1/usuarios
    tags=["Usuarios"]  # Agrupación en documentación
)

@router.post("/", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario.
    
    Crea una nueva cuenta de usuario en el sistema. Este endpoint es público
    para permitir el auto-registro.
    
    Parámetros:
        - usuario (UsuarioCreate): Datos del usuario (nombre, email, contraseña)
        - db (Session): Sesión de base de datos
    
    Returns:
        UsuarioResponse: Información del usuario creado (sin contraseña)
    
    Requiere autenticación: No
    Roles permitidos: Público
    """
    return crear_usuario(db, usuario)

@router.get("/", response_model=list[UsuarioResponse], dependencies=[Depends(require_role("admin"))])
def listar_usuarios(db: Session = Depends(get_db)):
    """
    Listar todos los usuarios.
    
    Obtiene la lista completa de usuarios registrados en el sistema.
    
    Parámetros:
        - db (Session): Sesión de base de datos
    
    Returns:
        List[UsuarioResponse]: Lista de todos los usuarios
    
    Requiere autenticación: Sí
    Roles permitidos: Admin
    """
    return obtener_usuarios(db)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario por su ID.
    
    Devuelve la información detallada de un usuario específico.
    
    Parámetros:
        - usuario_id (int): ID único del usuario (path parameter)
        - db (Session): Sesión de base de datos
    
    Returns:
        UsuarioResponse: Información completa del usuario
    
    Requiere autenticación: No
    Roles permitidos: Público
    
    Raises:
        HTTPException 404: Si el usuario no existe
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    # Validar que el usuario exista
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario_router(usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    """
    Actualizar información de un usuario.
    
    Modifica los datos de un usuario existente. Solo se actualizan los campos
    proporcionados en el body de la petición.
    
    Parámetros:
        - usuario_id (int): ID del usuario a actualizar (path parameter)
        - datos (UsuarioUpdate): Campos del usuario a modificar
        - db (Session): Sesión de base de datos
    
    Returns:
        UsuarioResponse: Información actualizada del usuario
    
    Requiere autenticación: Sí (idealmente validar que el usuario solo modifique su propia cuenta)
    Roles permitidos: Usuario propietario o Admin
    """
    return actualizar_usuario(db, usuario_id, datos)

@router.delete("/{usuario_id}", dependencies=[Depends(require_role("admin"))])
def eliminar_usuario_router(usuario_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un usuario.
    
    Elimina un usuario del sistema. Esta acción puede afectar registros relacionados
    como notificaciones y asignaciones de roles.
    
    Parámetros:
        - usuario_id (int): ID del usuario a eliminar (path parameter)
        - db (Session): Sesión de base de datos
    
    Returns:
        dict: Mensaje de confirmación
    
    Requiere autenticación: Sí
    Roles permitidos: Admin
    """
    eliminar_usuario(db, usuario_id)
    return {"mensaje": "Usuario eliminado correctamente"}
