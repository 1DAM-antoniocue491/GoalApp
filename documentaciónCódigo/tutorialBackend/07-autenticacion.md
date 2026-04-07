# Autenticación: ¿Quién Eres? (Para Principiantes)

## ¿Qué es la Autenticación?

Imagina que vas a un club nocturno:

```
┌─────────────────────────────────────────────┐
│                  PORTERO                     │
│                                            │
│   "Hola, ¿tienes tu pase VIP?"             │
│   "Déjame ver... ✅ Tu nombre está aquí"    │
│   "Puedes pasar"                            │
│                                            │
│   Si NO tienes pase → "No puedes entrar"    │
└─────────────────────────────────────────────┘
```

**La autenticación es igual:**
- El usuario quiere entrar a tu API
- El "portero" (tu API) verifica quién es
- Si es válido, le das un "pase" (token)
- El usuario muestra el pase en cada visita

---

## ¿Qué es un Token JWT?

### El Problema de las Sesiones Tradicionales

Antes, los websites usaban **sesiones**:

```
1. Usuario hace login
2. Servidor guarda: "Juan está logueado" (en memoria)
3. Servidor da una cookie: "sesion_id=abc123"
4. Usuario pide /perfil con la cookie
5. Servidor busca en memoria: "abc123 es Juan"
6. Servidor responde con el perfil de Juan
```

**Problema:**

- El servidor debe recordar TODAS las sesiones
- Si tienes 10,000 usuarios, necesitas memoria para 10,000 sesiones
- Si tienes múltiples servidores, deben compartir las sesiones

### La Solución: JWT (JSON Web Token)

JWT es como un **pase VIP** que el usuario lleva consigo:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JWT TOKEN                                    │
├─────────────────────────────────────────────────────────────────────┤
│  HEADER           │  PAYLOAD              │  SIGNATURE              │
│  {"alg":"HS256"}  │  {"sub":"1","exp":...} │  (firma del servidor)  │
│  (algoritmo)      │  (datos del usuario)  │  (prueba de autenticidad)│
└─────────────────────────────────────────────────────────────────────┘
```

**El flujo:**

```
1. Usuario hace login con email y password
2. Servidor verifica que son correctos
3. Servidor CREA un token con datos: {"sub":"1", "nombre":"Juan"}
4. Servidor FIRMA el token con una clave secreta
5. Servidor envía el token al usuario
6. Usuario guarda el token (en localStorage, memoria, etc.)
7. Usuario pide /perfil con el header: Authorization: Bearer <token>
8. Servidor VERIFICA la firma (¿quién creó este token?)
9. Servidor lee el payload (¿quién es el usuario?)
10. Servidor responde con el perfil
```

**Ventajas:**

- El servidor NO guarda sesiones (stateless)
- Escala mejor (cualquier servidor puede verificar)
- Funciona con microservicios

---

## Estructura del Token JWT

Un JWT tiene **tres partes** separadas por puntos:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6Ikp1YW4iLCJleHAiOjE3MDAwMDAwMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│                                      │                                                  │
│         HEADER (base64)              │              PAYLOAD (base64)                  │     SIGNATURE
```

### HEADER

```json
{
  "alg": "HS256",   // Algoritmo de firma
  "typ": "JWT"      // Tipo de token
}
```

### PAYLOAD

```json
{
  "sub": "1",              // Subject (ID del usuario)
  "name": "Juan",          // Nombre
  "email": "juan@email.com",
  "exp": 1700000000,       // Expiración (timestamp)
  "iat": 1699900000        // Issued at (cuando se creó)
}
```

### SIGNATURE

```
HMACSHA256(
  base64(header) + "." + base64(payload),
  secret_key
)
```

**¿Por qué firmar?**

- Si alguien intenta cambiar el payload, la firma ya no coincide
- El servidor detecta que el token fue manipulado
- **NUNCA pongas datos sensibles en el payload** (cualquiera puede leerlo)

---

## Implementar JWT

### Instalar Dependencias

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

| Librería | Para qué sirve |
|----------|---------------|
| `python-jose` | Crear y verificar tokens JWT |
| `passlib[bcrypt]` | Hashear contraseñas |

### Configuración

```env
# .env
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Generar SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Genera algo como: jX9kL2mN4pQ8rT6vW3yZ5aB7cD9eF1gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0
```

**⚠️ NUNCA uses claves simples como "password123" o "mi_clave_secreta".**

### Crear Token

```python
# app/api/auth.py
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

def create_access_token(data: dict) -> str:
    """
    Crea un token JWT.

    Args:
        data: Datos a incluir en el token (ej: {"sub": "1"})

    Returns:
        Token JWT firmado
    """
    # Copiar los datos
    to_encode = data.copy()

    # Añadir fecha de expiración
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Crear y firmar el token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt
```

### Verificar Token

```python
# app/api/auth.py
from jose import jwt, JWTError

def verify_token(token: str) -> dict | None:
    """
    Verifica un token JWT.

    Args:
        token: Token JWT a verificar

    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

---

## Login

### Endpoint de Login

```python
# app/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.auth import create_access_token
from app.api.services.usuario_service import autenticar_usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y genera un token JWT.

    El frontend envía:
    - username: email del usuario
    - password: contraseña del usuario

    Devuelve:
    - access_token: token JWT
    - token_type: "bearer"
    """
    # 1. Verificar credenciales
    usuario = autenticar_usuario(db, form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    # 2. Crear token
    access_token = create_access_token(
        data={"sub": str(usuario.id_usuario)}
    )

    # 3. Devolver token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

### ¿Qué es OAuth2PasswordRequestForm?

Es un **formulario estándar** de OAuth2 que espera:

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=juan@email.com&password=mi_contraseña
```

**No es JSON, es form-data.**

Por eso en el frontend:

```javascript
// Frontend (JavaScript)
const formData = new FormData();
formData.append('username', email);  // OAuth2 usa "username" aunque sea email
formData.append('password', password);

const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    body: formData  // No es JSON
});
```

### Servicio de Autenticación

```python
# app/api/services/usuario_service.py
from passlib.context import CryptContext
from app.models.usuario import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashea una contraseña."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(password, hashed)

def autenticar_usuario(db: Session, email: str, password: str) -> Usuario | None:
    """
    Verifica si las credenciales son correctas.

    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano

    Returns:
        Usuario si las credenciales son correctas, None si no
    """
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    # 2. Si no existe, return None
    if not usuario:
        return None

    # 3. Verificar contraseña
    if not verify_password(password, usuario.contraseña_hash):
        return None

    # 4. Devolver usuario
    return usuario
```

**¿Por qué no dar mensajes específicos?**

```python
# ❌ MALO - Informa si el email existe
if not usuario:
    raise ValueError("Usuario no encontrado")  # El email NO existe
if not verify_password(password, usuario.contraseña_hash):
    raise ValueError("Contraseña incorrecta")  # El email SÍ existe

# ✅ BUENO - Mensaje genérico
if not usuario or not verify_password(password, usuario.contraseña_hash):
    return None  # No sabemos si fue el email o la contraseña
```

---

## Proteger Endpoints

### Obtener Usuario Actual

```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Extrae el usuario del token JWT.

    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    # 1. Decodificar token
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Token inválido")
    except JWTError:
        raise HTTPException(401, "Token inválido")

    # 2. Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id_usuario == int(user_id)).first()
    if usuario is None:
        raise HTTPException(401, "Usuario no encontrado")

    return usuario
```

**¿Qué hace OAuth2PasswordBearer?**

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
```

Automáticamente:

1. Busca el header `Authorization: Bearer <token>`
2. Extrae el token
3. Si no hay token, devuelve 401 automáticamente
4. Si hay token, lo pasa a tu función

**Sin OAuth2PasswordBearer:**

```python
@router.get("/me")
def mi_perfil(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "No autorizado")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Formato inválido")
    token = authorization.replace("Bearer ", "")
    # ... verificar token ...
```

**Con OAuth2PasswordBearer:**

```python
@router.get("/me")
def mi_perfil(token: str = Depends(oauth2_scheme)):
    # token ya está extraído del header
    # Si no hay token, ya devolvió 401
```

### Usar la Dependencia

```python
# app/api/routers/auth.py

@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(current_user = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado.

    Requiere header: Authorization: Bearer <token>
    """
    return current_user
```

**El flujo completo:**

```
1. Cliente envía: GET /auth/me
   Header: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

2. FastAPI ve Depends(get_current_user)

3. FastAPI ejecuta:
   a. oauth2_scheme extrae el token del header
   b. get_current_user decodifica el token
   c. get_current_user busca al usuario en la BD
   d. get_current_user devuelve el usuario

4. Si todo OK, el endpoint recibe current_user
5. Si algo falla, devuelve 401 automáticamente
```

---

## Verificar Roles

### Dependencia de Rol

```python
# app/api/dependencies.py
from app.models.usuario import Usuario

def require_role(role_name: str):
    """
    Verifica que el usuario tenga un rol específico.

    Args:
        role_name: Nombre del rol requerido (ej: "admin")

    Returns:
        Función que verifica el rol

    Raises:
        HTTPException: Si el usuario no tiene el rol
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        roles = [rol.nombre for rol in current_user.roles]
        if role_name not in roles:
            raise HTTPException(403, f"Se requiere rol '{role_name}'")
        return True

    return role_checker
```

### Usar la Dependencia de Rol

```python
# app/api/routers/ligas.py
from app.api.dependencies import get_db, require_role

@router.delete(
    "/{id_liga}",
    status_code=204,
    dependencies=[Depends(require_role("admin"))]
)
def eliminar_liga(id_liga: int, db: Session = Depends(get_db)):
    """
    Elimina una liga. Solo administradores.
    """
    eliminar_liga(db, id_liga)
```

**¿Qué pasa si el usuario NO es admin?**

1. `get_current_user` obtiene el usuario
2. `require_role("admin")` verifica si tiene el rol
3. Si NO tiene el rol → devuelve 403 Forbidden
4. Si tiene el rol → continúa al endpoint

---

## Recuperación de Contraseña

### Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. Usuario: "Olvidé mi contraseña"                                  │
│     POST /auth/forgot-password                                      │
│     {"email": "juan@email.com"}                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. Servidor:                                                       │
│     - Verifica que el email existe                                  │
│     - Genera un token único (válido 30 minutos)                    │
│     - Envía email con link: /reset-password?token=abc123            │
│     - Devuelve: {"mensaje": "Email enviado"}                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. Usuario: Abre el link del email                                 │
│     Muestra formulario para nueva contraseña                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. Usuario: "Nueva contraseña"                                      │
│     POST /auth/reset-password                                       │
│     {"token": "abc123", "new_password": "nueva123"}                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. Servidor:                                                       │
│     - Verifica que el token es válido y no expiró                   │
│     - Actualiza la contraseña                                       │
│     - Invalida el token (ya no se puede usar de nuevo)              │
│     - Devuelve: {"mensaje": "Contraseña actualizada"}                │
└─────────────────────────────────────────────────────────────────────┘
```

### Modelo de Token

```python
# app/models/token_recuperacion.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from app.database.connection import Base

class TokenRecuperacion(Base):
    __tablename__ = "tokens_recuperacion"

    id_token = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    token = Column(String(255), unique=True, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)
```

### Endpoint Forgot Password

```python
# app/api/routers/auth.py
import secrets
from datetime import datetime, timedelta
from fastapi import BackgroundTasks

@router.post("/forgot-password")
def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Solicita recuperación de contraseña.

    Envía un email con un link para restablecer la contraseña.
    """
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()

    # Siempre devolver el mismo mensaje (seguridad)
    if not usuario:
        return {"mensaje": "Si el email está registrado, recibirás instrucciones"}

    # 2. Generar token único
    token = secrets.token_urlsafe(32)
    fecha_expiracion = datetime.utcnow() + timedelta(minutes=30)

    # 3. Guardar token en la base de datos
    token_db = TokenRecuperacion(
        id_usuario=usuario.id_usuario,
        token=token,
        fecha_expiracion=fecha_expiracion
    )
    db.add(token_db)
    db.commit()

    # 4. Enviar email en segundo plano
    background_tasks.add_task(
        enviar_email_recuperacion,
        email_destino=usuario.email,
        token=token
    )

    return {"mensaje": "Si el email está registrado, recibirás instrucciones"}
```

### Endpoint Reset Password

```python
@router.post("/reset-password")
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Restablece la contraseña usando el token.
    """
    # 1. Buscar token válido
    token_db = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.token == request.token,
        TokenRecuperacion.usado == False,
        TokenRecuperacion.fecha_expiracion > datetime.utcnow()
    ).first()

    if not token_db:
        raise HTTPException(400, "Token inválido o expirado")

    # 2. Buscar usuario
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == token_db.id_usuario
    ).first()

    if not usuario:
        raise HTTPException(400, "Usuario no encontrado")

    # 3. Actualizar contraseña
    usuario.contraseña_hash = hash_password(request.nueva_contraseña)

    # 4. Marcar token como usado
    token_db.usado = True

    db.commit()

    return {"mensaje": "Contraseña actualizada"}
```

---

## Uso desde el Frontend

### Login

```javascript
// Frontend (JavaScript)
async function login(email, password) {
    const formData = new FormData();
    formData.append('username', email);  // OAuth2 usa "username"
    formData.append('password', password);

    const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error('Credenciales incorrectas');
    }

    const data = await response.json();
    // data = { access_token: "...", token_type: "bearer" }

    // Guardar token
    localStorage.setItem('token', data.access_token);

    return data;
}
```

### Petición Autenticada

```javascript
async function getProfile() {
    const token = localStorage.getItem('token');

    if (!token) {
        throw new Error('No autenticado');
    }

    const response = await fetch('/api/v1/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.status === 401) {
        // Token expirado o inválido
        localStorage.removeItem('token');
        throw new Error('Sesión expirada');
    }

    return response.json();
}
```

### Interceptor para Todas las Peticiones

```javascript
// Configurar un interceptor para añadir el token automáticamente
const api = axios.create({
    baseURL: '/api/v1'
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
```

---

## Resumen

Aprendiste:

1. **JWT** = Un pase firmado que el usuario lleva consigo
2. **Token** = Header + Payload + Signature (tres partes)
3. **Login** = Verificar credenciales y crear token
4. **Proteger endpoints** = Usar `Depends(get_current_user)`
5. **Roles** = Usar `Depends(require_role("admin"))`
6. **Recuperar contraseña** = Token único por email

**¿Listo para el siguiente paso?**

Ve a **08-testing.md** para aprender cómo probar tu aplicación.