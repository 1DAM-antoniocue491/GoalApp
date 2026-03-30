# Autenticación

## JWT (JSON Web Token)

JWT es un estándar para crear tokens de acceso que permiten autenticar usuarios de forma stateless.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JWT Token                                    │
├─────────────────────────────────────────────────────────────────────┤
│  Header (algoritmo)   │   Payload (datos)   │   Signature (firma)   │
│  {"alg": "HS256"}     │   {"sub": "1"}      │   (hash del token)     │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo de Autenticación

```
Cliente                    Servidor                 Base de Datos
   │                          │                          │
   │  POST /auth/login        │                          │
   │  {email, password}       │                          │
   │─────────────────────────▶│                          │
   │                          │  Buscar usuario          │
   │                          │─────────────────────────▶│
   │                          │◀─────────────────────────│
   │                          │                          │
   │                          │  Verificar contraseña    │
   │                          │  Generar JWT            │
   │                          │                          │
   │  {access_token, token_type}                         │
   │◀─────────────────────────│                          │
   │                          │                          │
   │  GET /usuarios/me        │                          │
   │  Authorization: Bearer <token>                      │
   │─────────────────────────▶│                          │
   │                          │  Verificar JWT           │
   │                          │  Extraer user_id        │
   │                          │─────────────────────────▶│
   │                          │◀─────────────────────────│
   │  {id_usuario, nombre, ...}                         │
   │◀─────────────────────────│                          │
```

## Configuración

### Variables de entorno

```env
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Generar clave secreta

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Dependencias

### Base de datos

```python
# app/api/dependencies.py
from app.database.connection import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Usuario actual

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
):
    """Extrae y valida el usuario del token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Token inválido")
    except JWTError:
        raise HTTPException(401, "Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(401, "Usuario no encontrado")

    return usuario
```

### Verificar rol

```python
def require_role(role_name: str):
    def role_checker(current_user = Depends(get_current_user)):
        roles = [rol.nombre for rol in current_user.roles]
        if role_name not in roles:
            raise HTTPException(403, f"Se requiere rol '{role_name}'")
        return True
    return role_checker
```

## Crear Token JWT

```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un token JWT de acceso."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## Router de Autenticación

```python
# app/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.dependencies import get_db, get_current_user, create_access_token
from app.api.services.usuario_service import autenticar_usuario
from app.schemas.usuario import UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y genera un token JWT.

    Usa OAuth2PasswordRequestForm que espera:
    - username: Email del usuario
    - password: Contraseña
    """
    usuario = autenticar_usuario(db, form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    access_token = create_access_token(
        data={"sub": str(usuario.id_usuario)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(current_user = Depends(get_current_user)):
    """Obtiene el perfil del usuario autenticado."""
    return current_user

@router.post("/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    """Renueva un token JWT."""
    from jose import jwt, JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(401, "Usuario no encontrado")

    nuevo_token = create_access_token({"sub": str(usuario.id_usuario)})

    return {
        "access_token": nuevo_token,
        "token_type": "bearer"
    }
```

## Recuperación de Contraseña

### Modelo de token

```python
# app/models/token_recuperacion.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

class TokenRecuperacion(Base):
    __tablename__ = "tokens_recuperacion"

    id_token = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    token = Column(String(255), unique=True, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)
```

### Servicio

```python
import secrets
from datetime import datetime, timedelta

def crear_token_recuperacion(db: Session, usuario_id: int) -> str:
    """Genera un token de recuperación."""
    token = secrets.token_urlsafe(32)
    fecha_expiracion = datetime.utcnow() + timedelta(minutes=30)

    token_db = TokenRecuperacion(
        id_usuario=usuario_id,
        token=token,
        fecha_expiracion=fecha_expiracion,
        usado=False
    )

    db.add(token_db)
    db.commit()
    return token

def validar_token_recuperacion(db: Session, token: str):
    """Valida un token de recuperación."""
    token_db = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.token == token,
        TokenRecuperacion.usado == False,
        TokenRecuperacion.fecha_expiracion > datetime.utcnow()
    ).first()

    if not token_db:
        return None

    return db.query(Usuario).filter(Usuario.id_usuario == token_db.id_usuario).first()
```

### Endpoints

```python
@router.post("/forgot-password")
def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Solicita recuperación de contraseña."""
    usuario = obtener_usuario_por_email(db, request.email)

    if usuario:
        token = crear_token_recuperacion(db, usuario.id_usuario)
        background_tasks.add_task(
            enviar_email_recuperacion,
            email_destino=usuario.email,
            token=token
        )

    return {"mensaje": "Si el email está registrado, recibirás instrucciones"}

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Restablece la contraseña."""
    usuario = validar_token_recuperacion(db, request.token)

    if not usuario:
        raise HTTPException(400, "Token inválido o expirado")

    cambiar_contrasena_usuario(db, usuario.id_usuario, request.nueva_contrasena)

    return {"mensaje": "Contraseña actualizada"}
```

## Proteger Endpoints

### Endpoint público

```python
@router.get("/")
def listar_ligas(db: Session = Depends(get_db)):
    """No requiere autenticación."""
    return obtener_ligas(db)
```

### Endpoint protegido

```python
@router.get("/me")
def mi_perfil(current_user = Depends(get_current_user)):
    """Requiere token JWT válido."""
    return current_user
```

### Endpoint protegido por rol

```python
@router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    """Requiere rol 'admin'."""
    eliminar_usuario(db, id)
```

## Uso desde Cliente

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=juan@email.com&password=mi_contraseña"

# Respuesta
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Petición autenticada

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### JavaScript

```javascript
// Login
const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        body: formData
    });

    const { access_token } = await response.json();
    localStorage.setItem('token', access_token);
};

// Petición autenticada
const getProfile = async () => {
    const token = localStorage.getItem('token');

    const response = await fetch('/api/v1/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    return response.json();
};
```