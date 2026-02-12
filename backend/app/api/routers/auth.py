# app/api/routers/auth.py
"""
Router de Autenticación - Gestión de autenticación y autorización.
Endpoints para login, obtención de usuario actual y renovación de tokens JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.dependencies import (
    get_db,
    get_current_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)

from app.api.services.usuario_service import autenticar_usuario
from app.schemas.usuario import UsuarioResponse

# Configuración del router
router = APIRouter(
    prefix="/auth",  # Base path: /api/v1/auth
    tags=["Autenticación"]  # Agrupación en documentación
)

# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autenticar usuario y generar token de acceso.
    
    Valida las credenciales del usuario (email y contraseña) y genera un token JWT
    para acceder a los endpoints protegidos de la API.
    
    Parámetros:
        - form_data (OAuth2PasswordRequestForm): Formulario con username (email) y password
        - db (Session): Sesión de base de datos
    
    Returns:
        dict: Token de acceso JWT y tipo de token
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer"
        }
    
    Requiere autenticación: No
    Roles permitidos: Público
    
    Raises:
        HTTPException 401: Si las credenciales son incorrectas
    """
    # Autenticar usuario mediante servicio
    usuario = autenticar_usuario(db, form_data.username, form_data.password)

    # Validar que el usuario exista y la contraseña sea correcta
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    # Configurar tiempo de expiración del token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Crear token JWT con el ID del usuario
    access_token = create_access_token(
        data={"sub": str(usuario.id_usuario)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ============================================================
# USUARIO ACTUAL
# ============================================================

@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(current_user = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado.
    
    Devuelve los datos completos del usuario que está actualmente autenticado
    mediante el token JWT proporcionado en el header Authorization.
    
    Parámetros:
        - current_user: Usuario autenticado obtenido del token JWT
    
    Returns:
        UsuarioResponse: Información completa del usuario autenticado
    
    Requiere autenticación: Sí
    Roles permitidos: Todos los usuarios autenticados
    """
    return current_user

# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post("/refresh")
def refresh_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Renovar token de acceso usando un refresh token.
    
    Valida un refresh token y genera un nuevo access token si el refresh token
    es válido y el usuario aún existe en el sistema.
    
    Parámetros:
        - token (str): Refresh token JWT válido
        - db (Session): Sesión de base de datos
    
    Returns:
        dict: Nuevo token de acceso JWT
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer"
        }
    
    Requiere autenticación: No (pero requiere refresh token válido)
    Roles permitidos: Público
    
    Raises:
        HTTPException 401: Si el refresh token es inválido o el usuario no existe
    """
    from jose import jwt, JWTError

    try:
        # Decodificar el refresh token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        # Validar que el token contenga el ID de usuario
        if user_id is None:
            raise HTTPException(401, "Refresh token inválido")

    except JWTError:
        raise HTTPException(401, "Refresh token inválido")

    # Buscar usuario en la base de datos
    from app.api.services.usuario_service import obtener_usuario_por_id
    usuario = obtener_usuario_por_id(db, user_id)

    # Validar que el usuario exista
    if not usuario:
        raise HTTPException(401, "Refresh token inválido")

    # Crear nuevo access token
    nuevo_access_token = create_access_token({"sub": str(usuario.id_usuario)})

    return {
        "access_token": nuevo_access_token,
        "token_type": "bearer"
    }
