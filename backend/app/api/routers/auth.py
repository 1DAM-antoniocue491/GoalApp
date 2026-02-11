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

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
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
    Recibe email y contraseña y devuelve un access token JWT.
    """
    usuario = autenticar_usuario(db, form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

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
    Devuelve los datos del usuario autenticado.
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
    Recibe un refresh token y devuelve un nuevo access token.
    """
    from jose import jwt, JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, "Refresh token inválido")

    except JWTError:
        raise HTTPException(401, "Refresh token inválido")

    # Buscar usuario
    from app.api.services.usuario_service import obtener_usuario_por_id
    usuario = obtener_usuario_por_id(db, user_id)

    if not usuario:
        raise HTTPException(401, "Refresh token inválido")

    # Crear nuevo access token
    nuevo_access_token = create_access_token({"sub": str(usuario.id_usuario)})

    return {
        "access_token": nuevo_access_token,
        "token_type": "bearer"
    }
