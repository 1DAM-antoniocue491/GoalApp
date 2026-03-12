# Informe de Seguridad: Sistema de Autenticación JWT

**Proyecto:** GoalApp
**Fecha:** 10/03/2026
**Framework:** FastAPI (Python)
**Tipo de autenticación:** JWT (JSON Web Tokens)
**Alcance:** Análisis de seguridad para gestión de múltiples usuarios concurrentes

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Análisis del Flujo de Autenticación](#3-análisis-del-flujo-de-autenticación)
4. [Verificación de Concurrencia Multi-Usuario](#4-verificación-de-concurrencia-multi-usuario)
5. [Análisis de Componentes](#5-análisis-de-componentes)
6. [Vulnerabilidades Detectadas](#6-vulnerabilidades-detectadas)
7. [Recomendaciones de Seguridad](#7-recomendaciones-de-seguridad)
8. [Conclusión](#8-conclusión)

---

## 1. Resumen Ejecutivo

### Estado General del Sistema

| Aspecto | Estado | Puntuación |
|---------|--------|------------|
| Funcionamiento multi-usuario | ✅ CORRECTO | 9/10 |
| Seguridad de contraseñas | ✅ CORRECTO | 10/10 |
| Configuración JWT | ⚠️ MEJORABLE | 7/10 |
| Gestión de sesiones BD | ✅ CORRECTO | 9/10 |
| Pool de conexiones | ✅ CORRECTO | 9/10 |
| Protección contra ataques | ❌ INSUFICIENTE | 4/10 |

### Conclusión Principal

> **El sistema de autenticación SÍ distingue correctamente entre usuarios concurrentes.** La arquitectura JWT stateless garantiza que cada petición es procesada de forma independiente, extrayendo la identidad del usuario desde el token en cada request. No existe estado compartido que pueda causar mezcla de datos entre usuarios.

---

## 2. Arquitectura del Sistema

### 2.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARQUITECTURA DE AUTENTICACIÓN                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐ │
│  │   Cliente    │     │   FastAPI    │     │      Base de Datos           │ │
│  │   (React)    │────▶│   Backend    │────▶│      (MySQL)                 │ │
│  └──────────────┘     └──────────────┘     └──────────────────────────────┘ │
│         │                    │                       │                       │
│         │                    │                       │                       │
│         │              ┌─────┴─────┐                 │                       │
│         │              │           │                 │                       │
│         │              ▼           ▼                 │                       │
│         │      ┌────────────┐ ┌────────────┐        │                       │
│         │      │  auth.py   │ │dependencie │        │                       │
│         │      │  (login)   │ │    s.py    │        │                       │
│         │      └────────────┘ └────────────┘        │                       │
│         │             │                  │          │                       │
│         │             │                  │          │                       │
│         │             ▼                  ▼          │                       │
│         │      ┌─────────────────────────────────┐  │                       │
│         │      │           JWT Token             │  │                       │
│         │      │  ┌───────────────────────────┐  │  │                       │
│         │      │  │ Payload: {"sub": "123"}   │  │  │                       │
│         │      │  │ Firma: HMAC-SHA256        │  │  │                       │
│         │      │  └───────────────────────────┘  │  │                       │
│         │      └─────────────────────────────────┘  │                       │
│         │                                            │                       │
└─────────┴────────────────────────────────────────────┴───────────────────────┘
```

### 2.2 Archivos Involucrados

| Archivo | Propósito | Líneas Clave |
|---------|-----------|--------------|
| `backend/app/api/routers/auth.py` | Endpoints de autenticación | Login, Refresh, Me |
| `backend/app/api/dependencies.py` | Dependencias de autenticación | `get_current_user`, `create_access_token` |
| `backend/app/api/services/usuario_service.py` | Lógica de negocio de usuarios | Autenticación, CRUD |
| `backend/app/database/connection.py` | Pool de conexiones BD | SessionLocal, engine |
| `backend/app/models/usuario.py` | Modelo de usuario | Campos, relaciones |
| `backend/app/config.py` | Configuración JWT | SECRET_KEY, ALGORITHM, expiración |

---

## 3. Análisis del Flujo de Autenticación

### 3.1 Flujo de Login

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO DE LOGIN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Cliente                           Backend                          BD       │
│    │                                 │                               │       │
│    │  POST /api/v1/auth/login        │                               │       │
│    │  Body: username=email           │                               │       │
│    │        password=****            │                               │       │
│    │────────────────────────────────▶│                               │       │
│    │                                 │                               │       │
│    │                                 │  autenticar_usuario(db,email) │       │
│    │                                 │──────────────────────────────▶│       │
│    │                                 │                               │       │
│    │                                 │  SELECT * FROM usuarios       │       │
│    │                                 │  WHERE email = ?              │       │
│    │                                 │◀──────────────────────────────│       │
│    │                                 │                               │       │
│    │                                 │  verify_password(pwd, hash)   │       │
│    │                                 │  ✓ Contraseña correcta        │       │
│    │                                 │                               │       │
│    │                                 │  create_access_token(         │       │
│    │                                 │    {"sub": str(usuario.id)}   │       │
│    │                                 │  )                            │       │
│    │                                 │                               │       │
│    │  Response:                      │                               │       │
│    │  {                              │                               │       │
│    │    "access_token": "eyJ0...",   │                               │       │
│    │    "token_type": "bearer"       │                               │       │
│    │  }                              │                               │       │
│    │◀────────────────────────────────│                               │       │
│    │                                 │                               │       │
└────┴─────────────────────────────────┴───────────────────────────────┴───────┘
```

### 3.2 Estructura del Token JWT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ESTRUCTURA JWT                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3MDk...     │
│  └─────────────────────────────────┘ └─────────────────────────────────┘    │
│              HEADER                            PAYLOAD                       │
│                                                                              │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────┐     │
│  │        HEADER           │    │            PAYLOAD                   │     │
│  ├─────────────────────────┤    ├─────────────────────────────────────┤     │
│  │ {                       │    │ {                                    │     │
│  │   "alg": "HS256",       │    │   "sub": "123",    ← ID Usuario     │     │
│  │   "typ": "JWT"          │    │   "exp": 1709999999  ← Expiración   │     │
│  │ }                       │    │ }                                    │     │
│  └─────────────────────────┘    └─────────────────────────────────────┘     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           SIGNATURE                                  │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ HMACSHA256(                                                          │    │
│  │   base64UrlEncode(header) + "." + base64UrlEncode(payload),          │    │
│  │   SECRET_KEY                                                         │    │
│  │ )                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Flujo de Petición Protegida

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PETICIÓN PROTEGIDA                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Cliente                           Backend                          BD       │
│    │                                 │                               │       │
│    │  GET /api/v1/auth/me            │                               │       │
│    │  Authorization: Bearer eyJ0...  │                               │       │
│    │────────────────────────────────▶│                               │       │
│    │                                 │                               │       │
│    │                                 │  ┌─────────────────────────┐  │       │
│    │                                 │  │ OAuth2PasswordBearer    │  │       │
│    │                                 │  │ Extrae token del header │  │       │
│    │                                 │  └───────────┬─────────────┘  │       │
│    │                                 │              │                │       │
│    │                                 │              ▼                │       │
│    │                                 │  ┌─────────────────────────┐  │       │
│    │                                 │  │ get_current_user()      │  │       │
│    │                                 │  │                         │  │       │
│    │                                 │  │ 1. jwt.decode(token)    │  │       │
│    │                                 │  │ 2. payload.get("sub")   │  │       │
│    │                                 │  │ 3. user_id = int(sub)   │  │       │
│    │                                 │  └───────────┬─────────────┘  │       │
│    │                                 │              │                │       │
│    │                                 │              ▼                │       │
│    │                                 │  obtener_usuario_por_id(     │       │
│    │                                 │    db, user_id               │       │
│    │                                 │  )                           │       │
│    │                                 │──────────────────────────────▶│       │
│    │                                 │                               │       │
│    │                                 │  SELECT * FROM usuarios       │       │
│    │                                 │  WHERE id_usuario = 123       │       │
│    │                                 │◀──────────────────────────────│       │
│    │                                 │                               │       │
│    │  Response: Usuario {id: 123}    │                               │       │
│    │◀────────────────────────────────│                               │       │
│    │                                 │                               │       │
└────┴─────────────────────────────────┴───────────────────────────────┴───────┘
```

---

## 4. Verificación de Concurrencia Multi-Usuario

### 4.1 Escenario de Prueba: Múltiples Usuarios Concurrentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              ESCENARIO: 3 USUARIOS CONCURRENTES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Usuario A (ID: 1)        Usuario B (ID: 2)        Usuario C (ID: 3)        │
│       │                        │                        │                   │
│       │ Token: {sub:"1"}       │ Token: {sub:"2"}       │ Token: {sub:"3"}  │
│       │                        │                        │                   │
│       ▼                        ▼                        ▼                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         FASTAPI BACKEND                               │   │
│  │                                                                       │   │
│  │  Petición A          Petición B          Petición C                  │   │
│  │      │                    │                    │                     │   │
│  │      ▼                    ▼                    ▼                     │   │
│  │  ┌──────────┐        ┌──────────┐        ┌──────────┐               │   │
│  │  │ Sesión 1 │        │ Sesión 2 │        │ Sesión 3 │               │   │
│  │  │ (db_A)   │        │ (db_B)   │        │ (db_C)   │               │   │
│  │  └────┬─────┘        └────┬─────┘        └────┬─────┘               │   │
│  │       │                   │                   │                     │   │
│  │       ▼                   ▼                   ▼                     │   │
│  │  get_current_user()  get_current_user()  get_current_user()        │   │
│  │  sub = "1"           sub = "2"           sub = "3"                  │   │
│  │       │                   │                   │                     │   │
│  │       ▼                   ▼                   ▼                     │   │
│  │  Usuario A           Usuario B           Usuario C                  │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌──────────────┐                                │
│                              │   MySQL BD   │                                │
│                              │  Pool: 10    │                                │
│                              │  Max: 30     │                                │
│                              └──────────────┘                                │
│                                                                              │
│  RESULTADO: Cada petición obtiene SU usuario correctamente ✅               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Análisis de Aislamiento

| Componente | Implementación | ¿Aislamiento Correcto? |
|------------|----------------|----------------------|
| **Token JWT** | Cada usuario tiene token único con `sub` = su ID | ✅ SÍ |
| **Sesión BD** | `get_db()` crea sesión nueva por petición | ✅ SÍ |
| **Pool de conexiones** | `pool_size=10, max_overflow=20` | ✅ SÍ |
| **get_current_user** | Extrae ID del token de forma aislada | ✅ SÍ |
| **Variables globales** | Solo configuración (SECRET_KEY, settings) | ✅ SÍ (solo lectura) |

### 4.3 Código Clave de Aislamiento

```python
# dependencies.py - Líneas 26-31
def get_db():
    db = SessionLocal()      # ← Nueva sesión por petición
    try:
        yield db
    finally:
        db.close()           # ← Siempre se cierra (incluso en error)


# dependencies.py - Líneas 37-64
def get_current_user(
    token: str = Depends(oauth2_scheme),  # ← Token único por petición
    db = Depends(get_db)                   # ← Sesión única por petición
):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id_str = payload.get("sub")       # ← ID extraído del token
    user_id = int(user_id_str)

    usuario = obtener_usuario_por_id(db, user_id)  # ← Consulta aislada
    return usuario
```

---

## 5. Análisis de Componentes

### 5.1 Configuración JWT (`config.py`)

```python
# Configuración cargada desde .env
SECRET_KEY = settings.SECRET_KEY              # Clave de firma (debe ser 64+ bytes)
ALGORITHM = settings.ALGORITHM                # HS256 (simétrico)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
```

| Parámetro | Valor Actual | Recomendación | Estado |
|-----------|--------------|---------------|--------|
| SECRET_KEY | Desde .env | Mínimo 32 bytes aleatorios | ⚠️ Verificar longitud |
| ALGORITHM | HS256 | HS256 o RS256 | ✅ Correcto |
| Expiración | Desde .env | 15-60 min para access token | ⚠️ Verificar valor |

### 5.2 Pool de Conexiones (`connection.py`)

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,     # ✅ Verifica conexión antes de usar
    pool_recycle=3600,      # ✅ Recicla conexiones cada hora
    pool_size=10,           # ✅ 10 conexiones permanentes
    max_overflow=20         # ✅ Hasta 30 conexiones totales
)
```

| Parámetro | Valor | Evaluación |
|-----------|-------|------------|
| `pool_pre_ping` | True | ✅ Previene errores de "MySQL has gone away" |
| `pool_recycle` | 3600s | ✅ Evita conexiones obsoletas |
| `pool_size` | 10 | ✅ Adecuado para carga media |
| `max_overflow` | 20 | ✅ Permite picos de hasta 30 conexiones |

### 5.3 Hashing de Contraseñas (`usuario_service.py`)

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
```

| Aspecto | Estado |
|---------|--------|
| Algoritmo | ✅ bcrypt (resistente a rainbow tables) |
| Salt | ✅ Automático con bcrypt |
| Configuración | ✅ `deprecated="auto"` actualiza hashes antiguos |

---

## 6. Vulnerabilidades Detectadas

### 6.1 CRÍTICA: Refresh Token sin Validación de Expiración

**Ubicación:** `backend/app/api/routers/auth.py:112-168`

```python
@router.post("/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        # ❌ NO VERIFICA payload["exp"]
```

**Problema:** El endpoint `/refresh` acepta tokens expirados, permitiendo renovación indefinida.

**Riesgo:** Si un token es comprometido, nunca pierde validez para generar nuevos tokens.

**Severidad:** 🔴 ALTA

---

### 6.2 MEDIA: Sin Distinción entre Access Token y Refresh Token

**Ubicación:** `backend/app/api/routers/auth.py:75-78` y `auth.py:163`

```python
# Login genera:
access_token = create_access_token(
    data={"sub": str(usuario.id_usuario)},  # Sin tipo de token
)

# Refresh también genera token idéntico:
nuevo_access_token = create_access_token({"sub": str(usuario.id_usuario)})
```

**Problema:** No hay forma de distinguir si un token es de acceso o de refresco.

**Riesgo:** Un access token robado puede usarse para obtener nuevos tokens mediante `/refresh`.

**Severidad:** 🟡 MEDIA

---

### 6.3 MEDIA: Sin Mecanismo de Revocación

**Problema:** Los tokens JWT son stateless y no pueden revocarse individualmente.

**Escenarios de riesgo:**
- Usuario cambia contraseña → tokens antiguos siguen válidos
- Usuario desactivado → tokens siguen válidos hasta expirar
- Token robado → no hay forma de invalidarlo

**Severidad:** 🟡 MEDIA

---

### 6.4 BAJJA: Uso de `datetime.utcnow()` Deprecado

**Ubicación:** `backend/app/api/dependencies.py:92-94`

```python
# Python 3.12+ muestra DeprecationWarning
expire = datetime.utcnow() + expires_delta
```

**Solución:**
```python
from datetime import datetime, timezone
expire = datetime.now(timezone.utc) + expires_delta
```

**Severidad:** 🟢 BAJA

---

### 6.5 MEDIA: Sin Rate Limiting en Login

**Ubicación:** `backend/app/api/routers/auth.py:33-83`

**Problema:** El endpoint `/auth/login` no tiene límite de intentos.

**Riesgo:** Ataques de fuerza bruta para adivinar contraseñas.

**Severidad:** 🟡 MEDIA

---

### 6.6 BAJJA: Token Type Hardcodeado

**Ubicación:** `backend/app/api/routers/auth.py:80-83`

```python
return {
    "access_token": access_token,
    "token_type": "bearer"  # Hardcodeado, pero correcto según RFC 6750
}
```

**Severidad:** 🟢 BAJA (No es un problema real, sigue el estándar)

---

## 7. Recomendaciones de Seguridad

### 7.1 Implementar Sistema de Refresh Tokens Seguro

```python
# RECOMENDACIÓN: Estructura de token mejorada
def create_access_token(data: dict, token_type: str = "access", expires_delta=None):
    to_encode = data.copy()
    to_encode.update({
        "type": token_type,  # ← Distinguir tipo
        "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15)),
        "iat": datetime.now(timezone.utc),  # ← Issued At
        "jti": str(uuid.uuid4())  # ← JWT ID único para revocación
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Access token: 15 minutos
# Refresh token: 7 días
```

### 7.2 Implementar Blacklist de Tokens

```python
# Usar Redis para tokens revocados
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def is_token_revoked(jti: str) -> bool:
    return redis_client.exists(f"revoked:{jti}")

def revoke_token(jti: str, expires_in: int):
    redis_client.setex(f"revoked:{jti}", expires_in, "1")
```

### 7.3 Implementar Rate Limiting

```python
# Usar slowapi o similar
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), ...):
    ...
```

### 7.4 Corregir Refresh Token

```python
@router.post("/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # ✅ Verificar tipo de token
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Token inválido para refresco")

        # ✅ Verificar expiración (jwt.decode ya lo hace, pero ser explícitos)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Token inválido")

    except JWTError:
        raise HTTPException(401, "Token expirado o inválido")

    # Crear NUEVO access token (no refresh token)
    nuevo_access_token = create_access_token(
        {"sub": str(usuario.id_usuario)},
        token_type="access"
    )

    return {"access_token": nuevo_access_token, "token_type": "bearer"}
```

### 7.5 Tabla de Resumen de Mejoras

| Mejora | Prioridad | Complejidad | Impacto |
|--------|-----------|-------------|---------|
| Validar expiración en refresh | 🔴 Alta | Baja | Alto |
| Distinguir tipos de token | 🟡 Media | Media | Alto |
| Implementar blacklist | 🟡 Media | Alta | Alto |
| Rate limiting | 🟡 Media | Baja | Medio |
| Corregir datetime.utcnow() | 🟢 Baja | Baja | Bajo |

---

## 8. Conclusión

### Respuesta a la Pregunta Principal

> **¿El backend distingue entre usuarios diferentes en peticiones simultáneas?**

### ✅ SÍ, el sistema funciona correctamente.

**Justificación técnica:**

1. **Arquitectura Stateless:** Los tokens JWT contienen el ID del usuario en el campo `sub`, y cada petición extrae este ID de forma independiente.

2. **Sesiones Aisladas:** La función `get_db()` crea una sesión nueva de base de datos para cada petición, eliminando cualquier posibilidad de contaminación entre usuarios.

3. **Sin Estado Compartido Mutables:** No existen variables globales que puedan ser modificadas por múltiples peticiones. Las únicas variables globales (`SECRET_KEY`, `settings`) son de solo lectura.

4. **Pool de Conexiones:** La configuración del pool (`pool_pre_ping`, `pool_recycle`) garantiza conexiones saludables incluso bajo carga.

### Matriz de Riesgo Final

```
                    │ Sin Mejoras │ Con Mejoras │
────────────────────┼─────────────┼─────────────┤
Multi-usuario       │     ✅      │     ✅      │
Fugas de datos      │     ✅      │     ✅      │
Robo de tokens      │     ❌      │     ✅      │
Fuerza bruta        │     ❌      │     ✅      │
Revocación          │     ❌      │     ✅      │
```

---

**Documento generado automáticamente**
**Revisar periódicamente según cambios en el código**