# Implementación JWT en el Backend - Guía Completa

**Proyecto:** GoalApp
**Fecha:** 10/03/2026
**Framework:** FastAPI (Python 3.10+)

---

## Índice

1. [Visión General](#1-visión-general)
2. [Dependencias Necesarias](#2-dependencias-necesarias)
3. [Configuración](#3-configuración)
4. [Componentes del Sistema JWT](#4-componentes-del-sistema-jwt)
5. [Flujo Completo de Autenticación](#5-flujo-completo-de-autenticación)
6. [Código Paso a Paso](#6-código-paso-a-paso)
7. [Endpoints de Autenticación](#7-endpoints-de-autenticación)
8. [Protección de Rutas](#8-protección-de-rutas)
9. [Sistema de Roles](#9-sistema-de-roles)
10. [Base de Datos y Usuarios](#10-base-de-datos-y-usuarios)

---

## 1. Visión General

### ¿Qué es JWT?

JWT (JSON Web Token) es un estándar abierto (RFC 7519) para crear tokens de acceso que permiten transmitir información entre partes de forma segura. En este proyecto se usa para autenticar usuarios y proteger endpoints de la API.

### Arquitectura de Autenticación

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA JWT - GoalApp                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    Cliente                        Backend                          BD   │
│      │                              │                              │    │
│      │  1. POST /auth/login         │                              │    │
│      │  (email + password)          │                              │    │
│      │─────────────────────────────▶│                              │    │
│      │                              │  2. Validar credenciales     │    │
│      │                              │─────────────────────────────▶│    │
│      │                              │                              │    │
│      │                              │  3. Usuario encontrado       │    │
│      │                              │◀─────────────────────────────│    │
│      │                              │                              │    │
│      │                              │  4. create_access_token()    │    │
│      │                              │     payload: {"sub": user_id}│    │
│      │                              │                              │    │
│      │  5. JWT Token                │                              │    │
│      │◀─────────────────────────────│                              │    │
│      │                              │                              │    │
│      │  6. GET /auth/me             │                              │    │
│      │  Header: Authorization:      │                              │    │
│      │         Bearer <token>       │                              │    │
│      │─────────────────────────────▶│                              │    │
│      │                              │  7. get_current_user()       │    │
│      │                              │     - Decodifica JWT         │    │
│      │                              │     - Extrae user_id         │    │
│      │                              │     - Busca en BD            │    │
│      │                              │                              │    │
│      │  8. Datos del usuario        │                              │    │
│      │◀─────────────────────────────│                              │    │
│      │                              │                              │    │
└──────┴──────────────────────────────┴──────────────────────────────┴────┘
```

---

## 2. Dependencias Necesarias

### requirements.txt

```txt
python-jose[cryptography]   # Para generar y validar JWT
passlib[bcrypt]             # Para hashear contraseñas
python-multipart            # Para formulario OAuth2 (login)
```

### Instalación

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### Explicación de librerías

| Librería | Propósito |
|----------|-----------|
| `python-jose` | Implementación JWT en Python. Permite codificar, decodificar y validar tokens |
| `passlib[bcrypt]` | Algoritmo de hashing bcrypt para contraseñas (resistente a rainbow tables) |
| `python-multipart` | Necesario para que FastAPI procese formularios OAuth2PasswordRequestForm |

---

## 3. Configuración

### 3.1 Archivo .env

```env
# Configuración JWT
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3.2 Generar SECRET_KEY segura

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Esto genera una clave de 64 bytes codificada en base64url (aproximadamente 86 caracteres).

### 3.3 Archivo config.py

**Ubicación:** `backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Seguridad JWT
    SECRET_KEY: str              # Clave para firmar tokens
    ALGORITHM: str               # Algoritmo (HS256 = HMAC SHA256)
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Tiempo de vida del token

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

**¿Por qué usar Pydantic Settings?**
- Carga variables de entorno automáticamente
- Valida tipos de datos
- Centraliza toda la configuración
- Facilita testing con diferentes configuraciones

---

## 4. Componentes del Sistema JWT

### Estructura de un Token JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3MDk5OTk5OTl9.abcdef123456
└──────────── HEADER ────────────┘ └────────── PAYLOAD ──────────┘ └─ SIGNATURE ─┘
```

#### HEADER (Base64Url)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### PAYLOAD (Base64Url)
```json
{
  "sub": "123",        // Subject = ID del usuario
  "exp": 1709999999    // Expiration timestamp
}
```

#### SIGNATURE
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### Archivos del Sistema JWT

```
backend/app/
├── config.py                    # SECRET_KEY, ALGORITHM, expiración
├── api/
│   ├── dependencies.py          # create_access_token(), get_current_user()
│   └── routers/
│       └── auth.py              # Endpoints: login, refresh, me
├── api/services/
│   └── usuario_service.py       # autenticar_usuario(), hash_password()
└── models/
    └── usuario.py               # Modelo de usuario
```

---

## 5. Flujo Completo de Autenticación

### Diagrama de Secuencia

```
┌────────┐          ┌─────────┐         ┌──────────────┐        ┌─────────┐
│Cliente │          │ auth.py │         │dependencies.py│        │usuario_ │
│        │          │         │         │              │        │service.py│
└───┬────┘          └────┬────┘         └──────┬───────┘        └────┬────┘
    │                    │                     │                     │
    │ POST /auth/login   │                     │                     │
    │ email + password   │                     │                     │
    │───────────────────▶│                     │                     │
    │                    │                     │                     │
    │                    │ autenticar_usuario()│                     │
    │                    │────────────────────┼────────────────────▶│
    │                    │                     │                     │
    │                    │                     │    verify_password()│
    │                    │                     │◀────────────────────│
    │                    │                     │                     │
    │                    │     Usuario OK      │                     │
    │                    │◀────────────────────┼─────────────────────│
    │                    │                     │                     │
    │                    │ create_access_token(│                     │
    │                    │   {"sub": user_id}) │                     │
    │                    │────────────────────▶│                     │
    │                    │                     │                     │
    │                    │   JWT Token         │                     │
    │                    │◀────────────────────│                     │
    │                    │                     │                     │
    │  {access_token,    │                     │                     │
    │   token_type}      │                     │                     │
    │◀───────────────────│                     │                     │
    │                    │                     │                     │
```

---

## 6. Código Paso a Paso

### 6.1 Hashing de Contraseñas

**Archivo:** `backend/app/api/services/usuario_service.py`

```python
from passlib.context import CryptContext

# Configurar contexto de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña.

    bcrypt automáticamente:
    - Genera un salt único
    - Aplica múltiples rondas (cost factor)
    - Almacena salt + hash en el resultado

    Ejemplo de hash bcrypt:
    $2b$12$KIXx8wJ7...$LqF5mZ9vN...
    │  │   │         │
    │  │   │         └─ Hash (31 caracteres)
    │  │   └─ Salt (22 caracteres)
    │  └─ Cost factor (2^12 rondas)
    └─ Versión de bcrypt
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.

    1. Extrae el salt del hash almacenado
    2. Hashea la contraseña con ese salt
    3. Compara resultado con hash almacenado
    """
    return pwd_context.verify(password, hashed)
```

### 6.2 Autenticación de Usuario

**Archivo:** `backend/app/api/services/usuario_service.py`

```python
from sqlalchemy.orm import Session
from app.models.usuario import Usuario

def autenticar_usuario(db: Session, email: str, password: str):
    """
    Autentica un usuario por email y contraseña.

    Retorna:
        - Usuario object si las credenciales son correctas
        - None si no existe o contraseña incorrecta

    Seguridad:
        - No revela si el email existe o no (mismo mensaje de error)
        - Timing-attack resistant (verify_password es constante-time)
    """
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return None

    # 2. Verificar contraseña
    if not verify_password(password, usuario.contraseña_hash):
        return None

    return usuario
```

### 6.3 Creación del Token JWT

**Archivo:** `backend/app/api/dependencies.py`

```python
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

# Importar configuración
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Crea un token JWT firmado.

    Args:
        data: Diccionario con datos a incluir (ej: {"sub": "123"})
        expires_delta: Tiempo de vida opcional

    Returns:
        str: Token JWT codificado

    Proceso:
        1. Copiar datos del payload
        2. Calcular timestamp de expiración
        3. Añadir "exp" al payload
        4. Codificar con SECRET_KEY y ALGORITHM
    """
    to_encode = data.copy()

    # Calcular expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Añadir expiración al payload
    to_encode.update({"exp": expire})

    # Codificar y firmar
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
```

### 6.4 Extracción del Usuario Actual

**Archivo:** `backend/app/api/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# Esquema OAuth2 - extrae token del header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
):
    """
    Dependencia que extrae y valida el usuario del token JWT.

    Proceso:
        1. OAuth2PasswordBearer extrae token del header
        2. Decodifica JWT y valida firma
        3. Extrae user_id del claim "sub"
        4. Busca usuario en base de datos
        5. Retorna usuario o lanza 401

    Raises:
        HTTPException 401: Token inválido, expirado o usuario no existe
    """
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2. Extraer user_id del claim "sub"
        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise credenciales_invalidas

        # 3. Convertir a entero
        user_id = int(user_id_str)

    except (JWTError, ValueError):
        # JWTError: token malformado, firma inválida, expirado
        # ValueError: "sub" no es un número válido
        raise credenciales_invalidas

    # 4. Buscar usuario en BD
    usuario = obtener_usuario_por_id(db, user_id)

    if usuario is None:
        raise credenciales_invalidas

    return usuario
```

### 6.5 Sesión de Base de Datos por Petición

**Archivo:** `backend/app/api/dependencies.py`

```python
from app.database.connection import SessionLocal

def get_db():
    """
    Dependencia que provee una sesión de BD única por petición.

    IMPORTANTE para multi-usuario:
        - Cada petición obtiene su propia sesión
        - La sesión se cierra SIEMPRE (incluso en error)
        - No hay estado compartido entre peticiones

    Esto garantiza que usuarios concurrentes
    no interfieran entre sí.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 7. Endpoints de Autenticación

**Archivo:** `backend/app/api/routers/auth.py`

### 7.1 Login

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica usuario y genera token JWT.

    OAuth2PasswordRequestForm espera:
        - username: en nuestro caso es el email
        - password: contraseña en texto plano

    Retorna:
        {"access_token": "...", "token_type": "bearer"}
    """
    # 1. Autenticar
    usuario = autenticar_usuario(db, form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    # 2. Configurar expiración
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 3. Crear token con ID del usuario
    access_token = create_access_token(
        data={"sub": str(usuario.id_usuario)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

### 7.2 Obtener Usuario Actual

```python
@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(current_user = Depends(get_current_user)):
    """
    Retorna información del usuario autenticado.

    get_current_user:
        - Extrae token del header
        - Valida y decodifica
        - Busca usuario en BD
        - Inyecta usuario en la función
    """
    return current_user
```

### 7.3 Refresh Token

```python
@router.post("/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Renueva el token de acceso.

    TODO: Actualmente no valida expiración del refresh token
    Ver ERRORES_SEGURIDAD_AUTENTICACION.md
    """
    from jose import jwt, JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, "Refresh token inválido")

    except JWTError:
        raise HTTPException(401, "Refresh token inválido")

    usuario = obtener_usuario_por_id(db, user_id)

    if not usuario:
        raise HTTPException(401, "Refresh token inválido")

    nuevo_access_token = create_access_token({"sub": str(usuario.id_usuario)})

    return {
        "access_token": nuevo_access_token,
        "token_type": "bearer"
    }
```

---

## 8. Protección de Rutas

### 8.1 Usando get_current_user

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/mis-datos")
def obtener_mis_datos(current_user: Usuario = Depends(get_current_user)):
    """
    Endpoint protegido. Solo accesible con token válido.

    Si no hay token o es inválido:
        → HTTP 401 Unauthorized
    """
    return {
        "id": current_user.id_usuario,
        "nombre": current_user.nombre,
        "email": current_user.email
    }
```

### 8.2 Endpoint Público vs Protegido

```python
# Público - sin Depends(get_current_user)
@router.get("/publico")
def endpoint_publico():
    return {"mensaje": "Acceso libre"}

# Protegido - requiere token
@router.get("/privado")
def endpoint_privado(current_user = Depends(get_current_user)):
    return {"mensaje": f"Hola, {current_user.nombre}"}
```

---

## 9. Sistema de Roles

### 9.1 Verificación de Roles

**Archivo:** `backend/app/api/dependencies.py`

```python
def require_role(role_name: str):
    """
    Factory de dependencia que verifica si el usuario tiene un rol.

    Uso:
        @router.delete("/usuarios/{id}",
                       dependencies=[Depends(require_role("Admin"))])
        def eliminar_usuario(id: int):
            ...

    Retorna:
        función dependencia que verifica el rol
    """
    def role_checker(current_user = Depends(get_current_user)):
        # Extraer nombres de roles del usuario
        roles = [rol.nombre for rol in current_user.roles]

        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol '{role_name}'"
            )
        return True

    return role_checker
```

### 9.2 Uso en Endpoints

```python
from app.api.dependencies import require_role

# Solo Admin puede eliminar usuarios
@router.delete("/usuarios/{id}")
def eliminar_usuario(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_role("Admin"))
):
    eliminar_usuario(db, id)
    return {"mensaje": "Usuario eliminado"}
```

---

## 10. Base de Datos y Usuarios

### 10.1 Modelo de Usuario

**Archivo:** `backend/app/models/usuario.py`

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    contraseña_hash = Column(String(255), nullable=False)

    # Relación N:N con roles
    roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")
```

### 10.2 Crear Usuario (Registro)

**Archivo:** `backend/app/api/services/usuario_service.py`

```python
def crear_usuario(db: Session, datos: UsuarioCreate):
    """
    Crea un nuevo usuario con contraseña hasheada.
    """
    # Verificar email único
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    # Crear usuario con hash de contraseña
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hash_password(datos.contraseña)
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario
```

### 10.3 Schema de Registro

**Archivo:** `backend/app/schemas/usuario.py`

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    contraseña: str  # En texto plano, se hashea al guardar

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str

    class Config:
        from_attributes = True  # Pydantic v2 (antes orm_mode)
```

---

## Resumen de Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `config.py` | SECRET_KEY, ALGORITHM, expiración |
| `dependencies.py` | `create_access_token()`, `get_current_user()`, `require_role()` |
| `auth.py` | Endpoints: login, refresh, me |
| `usuario_service.py` | `autenticar_usuario()`, `hash_password()`, `verify_password()` |
| `usuario.py` (model) | Modelo SQLAlchemy de usuario |
| `usuario.py` (schema) | Pydantic schemas para validación |

## Flujo de Datos Resumido

```
Registro:
  contraseña → hash_password() → contraseña_hash → BD

Login:
  email + password → autenticar_usuario() → verify_password()
  → create_access_token({"sub": user_id}) → JWT → Cliente

Petición protegida:
  Header: Authorization: Bearer <JWT>
  → get_current_user() → jwt.decode() → obtener_usuario_por_id()
  → Usuario inyectado en endpoint
```
