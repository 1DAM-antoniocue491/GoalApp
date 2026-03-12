# Errores de Seguridad: Sistema de Autenticación JWT

**Proyecto:** GoalApp
**Fecha:** 10/03/2026
**Archivo:** Referencia para futuras correcciones

---

## Resumen de Errores

| # | Severidad | Problema | Archivo | Línea |
|---|-----------|----------|---------|-------|
| 1 | 🔴 Alta | Refresh token no valida expiración | `auth.py` | 112-168 |
| 2 | 🟡 Media | Sin distinción access/refresh token | `auth.py` | 75-78, 163 |
| 3 | 🟡 Media | Sin mecanismo de revocación | Global | - |
| 4 | 🟡 Media | Sin rate limiting en login | `auth.py` | 33-83 |
| 5 | 🟢 Baja | `datetime.utcnow()` deprecado | `dependencies.py` | 92-94 |

---

## Error 1: Refresh Token sin Validación de Expiración

### 🔴 Severidad: ALTA

### Ubicación
```
Archivo: backend/app/api/routers/auth.py
Líneas: 112-168
Función: refresh_token()
```

### Código Actual
```python
@router.post("/refresh")
def refresh_token(
    token: str,
    db: Session = Depends(get_db)
):
    from jose import jwt, JWTError

    try:
        # Decodificar el refresh token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        # ❌ NO VERIFICA SI EL TOKEN HA EXPIRADO
        if user_id is None:
            raise HTTPException(401, "Refresh token inválido")

    except JWTError:
        raise HTTPException(401, "Refresh token inválido")
```

### Problema
`jwt.decode()` con `algorithms=[ALGORITHM]` NO verifica automáticamente la expiración si no se especifican opciones. Esto permite que tokens expirados generen nuevos tokens válidos indefinidamente.

### Impacto
- Tokens robados nunca pierden capacidad de renovación
- No hay límite temporal de seguridad
- Ataque de persistencia de sesión

### Solución
```python
from jose import jwt, JWTError, ExpiredSignatureError

@router.post("/refresh")
def refresh_token(
    token: str,
    db: Session = Depends(get_db)
):
    try:
        # ✅ Verificar explícitamente expiración
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require_exp": True}  # Exige campo exp
        )
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, "Refresh token inválido")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expirado"
        )
    except JWTError:
        raise HTTPException(401, "Refresh token inválido")

    # Resto del código...
```

---

## Error 2: Sin Distinción entre Access Token y Refresh Token

### 🟡 Severidad: MEDIA

### Ubicación
```
Archivo: backend/app/api/routers/auth.py
Líneas: 75-78 (login) y 163 (refresh)
```

### Código Actual
```python
# En login (línea 75-78):
access_token = create_access_token(
    data={"sub": str(usuario.id_usuario)},
    expires_delta=access_token_expires
)

# En refresh (línea 163):
nuevo_access_token = create_access_token({"sub": str(usuario.id_usuario)})
```

### Problema
Ambos tokens tienen la misma estructura `{"sub": "id", "exp": timestamp}`. No hay forma de distinguir si un token fue generado como access token o refresh token.

### Impacto
- Un access token robado puede usarse en `/refresh` para obtener tokens nuevos
- Un refresh token puede usarse como access token para acceder a endpoints protegidos
- Violación del principio de menor privilegio

### Solución
```python
# En dependencies.py - Modificar create_access_token:
def create_access_token(
    data: dict,
    token_type: str = "access",  # "access" o "refresh"
    expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    to_encode["type"] = token_type  # ✅ Añadir tipo

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Diferentes tiempos según tipo
        if token_type == "access":
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# En auth.py - Modificar get_current_user:
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # ✅ Verificar que es access token
        if payload.get("type") != "access":
            raise HTTPException(401, "Token inválido para acceso")

        user_id = payload.get("sub")
        # ...


# En auth.py - Modificar refresh_token:
@router.post("/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # ✅ Verificar que es refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Token inválido para refresco")

        # ...
```

---

## Error 3: Sin Mecanismo de Revocación de Tokens

### 🟡 Severidad: MEDIA

### Ubicación
```
Archivo: Global (arquitectura)
Funciones afectadas: create_access_token, get_current_user, refresh_token
```

### Problema
Los tokens JWT son stateless. Una vez emitidos, no pueden invalidarse hasta que expiren naturalmente.

### Escenarios Problemáticos
| Escenario | Comportamiento Actual | Riesgo |
|-----------|----------------------|--------|
| Usuario cambia contraseña | Tokens antiguos siguen válidos | Acceso no autorizado |
| Usuario desactivado/eliminado | Tokens siguen válidos | Acceso a cuenta inexistente |
| Token robado detectado | No hay forma de bloquearlo | Acceso continuo del atacante |
| Logout | Token sigue válido hasta expirar | Sesión no realmente cerrada |

### Solución: Implementar Blacklist con Redis

```python
# Nuevo archivo: backend/app/api/token_blacklist.py
import redis
from datetime import timedelta
from app.config import settings

# Cliente Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def add_token_to_blacklist(jti: str, expires_in_seconds: int):
    """Añade un token a la blacklist."""
    redis_client.setex(f"blacklist:{jti}", expires_in_seconds, "1")

def is_token_blacklisted(jti: str) -> bool:
    """Verifica si un token está en la blacklist."""
    return redis_client.exists(f"blacklist:{jti}")


# Modificar create_access_token para incluir jti:
import uuid

def create_access_token(data: dict, token_type: str = "access", expires_delta=None):
    to_encode = data.copy()
    to_encode["type"] = token_type
    to_encode["jti"] = str(uuid.uuid4())  # ✅ ID único del token

    # ... resto del código


# Modificar get_current_user:
def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")

        # ✅ Verificar blacklist
        if jti and is_token_blacklisted(jti):
            raise HTTPException(401, "Token revocado")

        # ... resto del código


# Nuevo endpoint de logout:
@router.post("/logout")
def logout(current_user = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload.get("jti")
    exp = payload.get("exp")

    if jti and exp:
        # Añadir a blacklist hasta que expire
        ttl = exp - datetime.now(timezone.utc).timestamp()
        if ttl > 0:
            add_token_to_blacklist(jti, int(ttl))

    return {"mensaje": "Sesión cerrada correctamente"}
```

---

## Error 4: Sin Rate Limiting en Login

### 🟡 Severidad: MEDIA

### Ubicación
```
Archivo: backend/app/api/routers/auth.py
Líneas: 33-83
Función: login()
```

### Código Actual
```python
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Sin límite de intentos
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    # ...
```

### Problema
No hay límite en el número de intentos de login. Un atacante puede realizar miles de intentos de fuerza bruta.

### Impacto
- Ataques de diccionario
- Ataques de fuerza bruta
- Enumeración de usuarios (diferentes mensajes de error)

### Solución: Implementar Rate Limiting

```python
# Opción 1: Usar slowapi
# Instalar: pip install slowapi

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# En main.py:
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# En auth.py:
@router.post("/login")
@limiter.limit("5/minute")  # ✅ Máximo 5 intentos por minuto por IP
def login(
    request: Request,  # Necesario para el rate limiter
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # ...


# Opción 2: Implementación manual simple
intentos_fallidos = {}  # En producción usar Redis

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    ip = request.client.host
    clave_intentos = f"login:{ip}"

    # Verificar límite
    if intentos_fallidos.get(clave_intentos, 0) >= 5:
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos. Espere 1 minuto."
        )

    usuario = autenticar_usuario(db, form_data.username, form_data.password)

    if not usuario:
        # Incrementar contador de intentos fallidos
        intentos_fallidos[clave_intentos] = intentos_fallidos.get(clave_intentos, 0) + 1
        raise HTTPException(401, "Credenciales incorrectas")

    # Resetear contador en login exitoso
    intentos_fallidos.pop(clave_intentos, None)

    # ... generar token
```

---

## Error 5: Uso de `datetime.utcnow()` Deprecado

### 🟢 Severidad: BAJA

### Ubicación
```
Archivo: backend/app/api/dependencies.py
Líneas: 92-94
Función: create_access_token()
```

### Código Actual
```python
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # ❌ Deprecado en Python 3.12+
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # ...
```

### Problema
`datetime.utcnow()` está deprecado desde Python 3.12. Genera warnings y será eliminado en versiones futuras.

### Solución
```python
from datetime import datetime, timezone, timedelta

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta  # ✅ Forma correcta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # ...
```

---

## Checklist de Correcciones

### Prioridad Alta
- [ ] Error 1: Validar expiración en refresh_token

### Prioridad Media
- [ ] Error 2: Añadir campo `type` a tokens
- [ ] Error 3: Implementar blacklist de tokens (requiere Redis)
- [ ] Error 4: Implementar rate limiting en login

### Prioridad Baja
- [ ] Error 5: Cambiar `datetime.utcnow()` por `datetime.now(timezone.utc)`

---

## Dependencias Requeridas para Soluciones

```txt
# requirements.txt - Añadir:
slowapi>=0.1.9      # Para rate limiting
redis>=4.5.0        # Para blacklist de tokens
```

---

## Archivos a Modificar

| Archivo | Errores a Corregir |
|---------|-------------------|
| `backend/app/api/routers/auth.py` | 1, 2, 4 |
| `backend/app/api/dependencies.py` | 2, 5 |
| `backend/app/config.py` | 3 (añadir REDIS_HOST, REDIS_PORT) |
| `backend/app/main.py` | 4 (añadir middleware rate limiting) |
| Nuevo: `backend/app/api/token_blacklist.py` | 3 |

---

*Este archivo sirve como referencia para futuras correcciones.*