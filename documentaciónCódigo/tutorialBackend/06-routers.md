# Routers: Los Endpoints HTTP (Para Principiantes)

## ¿Qué es un Router?

Imagina un restaurante:

```
┌─────────────────────────────────────────────┐
│                  MESERO                      │
│                                            │
│   "Hola, ¿qué desea ordenar?"              │
│   "Tengo hamburguesas, pizzas, ensaladas"   │
│   "¿Me trae la cuenta, por favor?"          │
│                                            │
│   El mesero NO cocina, solo toma pedidos    │
└─────────────────────────────────────────────┘
```

**Un router es como el mesero:**
- Recibe los pedidos (peticiones HTTP)
- Valida que el pedido esté bien
- Pasa el pedido a la cocina (service)
- Devuelve la respuesta al cliente

**El router NO prepara la comida**, solo la recibe y entrega.

---

## ¿Por qué Separar Routers?

### Sin Routers (❌ Todo en main.py)

```python
# main.py - ¡Un desastre!
@app.get("/api/v1/usuarios/")
def listar_usuarios(): ...

@app.post("/api/v1/usuarios/")
def crear_usuario(): ...

@app.get("/api/v1/ligas/")
def listar_ligas(): ...

@app.post("/api/v1/ligas/")
def crear_liga(): ...

# ... cientos de endpoints en un solo archivo
```

**Problemas:**
- Un archivo gigante
- Difícil de encontrar código
- Conflictos en equipo
- Sin organización

### Con Routers (✅ Organizado)

```python
# routers/usuarios.py - Solo endpoints de usuarios
router = APIRouter(prefix="/usuarios")

@router.get("/")
def listar(): ...

@router.post("/")
def crear(): ...

# routers/ligas.py - Solo endpoints de ligas
router = APIRouter(prefix="/ligas")

# main.py - Solo registro
app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(ligas.router, prefix="/api/v1")
```

**Ventajas:**
- Cada recurso en su archivo
- Fácil de encontrar
- Fácil de mantener
- Organización clara

---

## Crear un Router

### Estructura Básica

```python
# app/api/routers/usuarios.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db
from app.api.services.usuario_service import crear_usuario, obtener_usuarios
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

# Crear el router
router = APIRouter(
    prefix="/usuarios",    # Prefijo para todos los endpoints
    tags=["Usuarios"]      # Etiqueta para Swagger
)

@router.get("/")
def listar(db: Session = Depends(get_db)):
    """Lista todos los usuarios."""
    return obtener_usuarios(db)

@router.post("/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario."""
    return crear_usuario(db, datos)
```

### ¿Qué significa cada parte?

| Código | ¿Qué hace? |
|--------|------------|
| `APIRouter()` | Crea un grupo de endpoints |
| `prefix="/usuarios"` | Todos los endpoints empiezan con `/usuarios` |
| `tags=["Usuarios"]` | Agrupa en Swagger UI |
| `@router.get("/")` | Define un endpoint GET |
| `@router.post("/")` | Define un endpoint POST |

**Con `prefix="/usuarios"`:**

```python
@router.get("/")        # GET /usuarios/
@router.get("/{id}")    # GET /usuarios/{id}
@router.post("/")       # POST /usuarios/
@router.put("/{id}")    # PUT /usuarios/{id}
@router.delete("/{id}") # DELETE /usuarios/{id}
```

### Registrar el Router

```python
# app/main.py
from app.api.routers import usuarios, ligas, auth

app = FastAPI(title="Mi App")

# Registrar los routers
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(ligas.router, prefix="/api/v1", tags=["Ligas"])
```

**Resultado de las URLs:**

| Router | Prefijo en main | Prefijo en router | URL final |
|--------|-----------------|-------------------|-----------|
| auth | `/api/v1` | `/auth` | `/api/v1/auth/` |
| usuarios | `/api/v1` | `/usuarios` | `/api/v1/usuarios/` |
| ligas | `/api/v1` | `/ligas` | `/api/v1/ligas/` |

---

## Métodos HTTP

### ¿Qué es cada método?

| Método | Uso | Analogía |
|--------|-----|----------|
| **GET** | Obtener datos | Leer el menú |
| **POST** | Crear nuevo | Hacer un pedido |
| **PUT** | Reemplazar completo | Cambiar todo el pedido |
| **PATCH** | Actualizar parcial | Modificar parte del pedido |
| **DELETE** | Eliminar | Cancelar el pedido |

### GET - Obtener Datos

```python
# Obtener todos
@router.get("/", response_model=List[UsuarioResponse])
def listar(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos los usuarios con paginación."""
    return obtener_usuarios(db, skip=skip, limit=limit)

# Obtener uno por ID
@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    """Obtiene un usuario por su ID."""
    usuario = obtener_usuario_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
```

**¿Por qué paginación?**

```python
# ❌ Sin paginación
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).all()  # ¡Devuelve TODOS los usuarios!

# Si hay 1,000,000 de usuarios:
# - Respuesta gigante (cientos de MB)
# - Tiempo de respuesta muy lento
# - Agota la memoria del servidor

# ✅ Con paginación
@router.get("/")
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Usuario).offset(skip).limit(limit).all()
    # Solo devuelve 100 usuarios
```

**URLs con paginación:**

```
GET /usuarios?skip=0&limit=10    → Usuarios 1-10
GET /usuarios?skip=10&limit=10   → Usuarios 11-20
GET /usuarios?skip=20&limit=10  → Usuarios 21-30
```

### POST - Crear

```python
@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def crear(
    datos: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo usuario."""
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**¿Por qué `status_code=201`?**

| Código | Significado | Cuándo usar |
|--------|-------------|-------------|
| 200 OK | Operación exitosa | GET, PUT exitoso |
| 201 Created | Recurso creado | POST exitoso |
| 204 No Content | Sin contenido | DELETE exitoso |
| 400 Bad Request | Datos inválidos | Validación |
| 404 Not Found | No existe | Recurso no encontrado |
| 500 Server Error | Error interno | Error inesperado |

### PUT - Actualizar Completo

```python
@router.put("/{id_usuario}", response_model=UsuarioResponse)
def actualizar(
    id_usuario: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un usuario completamente."""
    try:
        usuario = actualizar_usuario(db, id_usuario, datos)
        return usuario
    except ValueError as e:
        if "no encontrado" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

**PUT vs PATCH:**

| Método | Semántica | Ejemplo |
|--------|-----------|---------|
| PUT | Reemplazar completo | Actualizar TODOS los campos |
| PATCH | Actualizar parcial | Actualizar SOLO los campos enviados |

```python
# PUT /usuarios/1
# Body: {"nombre": "Juan", "email": "juan@email.com", "telefono": "123"}
# Actualiza TODOS los campos

# PATCH /usuarios/1
# Body: {"telefono": "456"}
# Actualiza SOLO el teléfono, el resto se mantiene igual
```

### DELETE - Eliminar

```python
@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    """Elimina un usuario."""
    try:
        eliminar_usuario(db, id_usuario)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    # No devuelve nada (204 No Content)
```

**¿Por qué 204 y no 200?**

```python
# Con 200 OK
@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db)):
    eliminar_usuario(db, id)
    return {"mensaje": "Usuario eliminado"}  # Body innecesario

# Con 204 No Content
@router.delete("/{id}", status_code=204)
def eliminar(id: int, db: Session = Depends(get_db)):
    eliminar_usuario(db, id)
    # No devuelve nada, 204 indica éxito sin contenido
```

---

## Parámetros

### Path Parameters (En la URL)

```python
@router.get("/{id_usuario}")
def obtener(id_usuario: int, db: Session = Depends(get_db)):
    # id_usuario viene de la URL: /usuarios/123
    pass
```

**Path Parameters son obligatorios:**

```
GET /usuarios/123    → id_usuario = 123
GET /usuarios/abc    → Error: abc no es int (422)
GET /usuarios/       → Error: falta id_usuario (404)
```

**Validación de Path Parameters:**

```python
from fastapi import Path

@router.get("/{id_usuario}")
def obtener(
    id_usuario: int = Path(..., gt=0, description="ID del usuario")
):
    # gt=0: debe ser mayor que 0
    # Si id_usuario = -1 o 0, error 422
    pass
```

### Query Parameters (Después de ?)

```python
@router.get("/")
def listar(
    skip: int = 0,
    limit: int = 100,
    nombre: str | None = None,
    db: Session = Depends(get_db)
):
    # URL: /usuarios?skip=0&limit=10&nombre=Juan
    pass
```

**Query Parameters son opcionales (si tienen valor por defecto):**

```
GET /usuarios                    → skip=0, limit=100, nombre=None
GET /usuarios?limit=10          → skip=0, limit=10, nombre=None
GET /usuarios?nombre=Juan        → skip=0, limit=100, nombre="Juan"
GET /usuarios?skip=20&limit=10&nombre=Juan  → todos especificados
```

**Validación de Query Parameters:**

```python
from fastapi import Query

@router.get("/")
def listar(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros")
):
    # ge=0: mayor o igual a 0
    # le=1000: menor o igual a 1000
    # Si skip=-1 o limit=2000, error 422
    pass
```

### Body Parameters (En el cuerpo)

```python
@router.post("/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # datos viene del cuerpo de la petición
    # {
    #   "nombre": "Juan",
    #   "email": "juan@email.com",
    #   "password": "mi_contraseña"
    # }
    pass
```

**Pydantic valida automáticamente:**

```python
# Body correcto
{
    "nombre": "Juan",
    "email": "juan@email.com",
    "password": "mi_contraseña"
}
# ✅ Todo correcto

# Body incorrecto
{
    "nombre": "Ju",           # ❌ Mínimo 2 caracteres
    "email": "no-es-email",   # ❌ No es email
    "password": "123"         # ❌ Mínimo 6 caracteres
}
# Error 422 con detalles de cada error
```

---

## Dependencias

### ¿Qué es una Dependencia?

Una **dependencia** es algo que tu endpoint necesita para funcionar. Es como pedirle al mesero:

- "Necesito acceso a la cocina" → `db: Session`
- "Necesito saber quién hace el pedido" → `current_user: Usuario`

FastAPI te lo da automáticamente con `Depends()`.

### Dependencia de Base de Datos

```python
from app.api.dependencies import get_db

@router.get("/")
def listar(db: Session = Depends(get_db)):
    # db ya está creado y listo para usar
    return db.query(Usuario).all()
    # db se cierra automáticamente después
```

**¿Cómo funciona?**

```python
# app/api/dependencies.py
def get_db():
    db = SessionLocal()  # Crear conexión
    try:
        yield db        # Dar al endpoint
    finally:
        db.close()      # Cerrar siempre
```

**El flujo:**

```
1. FastAPI llama a get_db()
2. get_db() crea la conexión: db = SessionLocal()
3. yield db → el endpoint recibe db
4. El endpoint hace su trabajo
5. finally: db.close() → se cierra la conexión
```

### Dependencia de Usuario Autenticado

```python
from app.api.dependencies import get_current_user

@router.get("/me")
def mi_perfil(current_user = Depends(get_current_user)):
    # current_user ya está autenticado
    # Si no hay token o es inválido, ya devolvió 401
    return current_user
```

**¿Cómo funciona `get_current_user`?**

```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    1. Extrae el token del header Authorization: Bearer <token>
    2. Verifica que el token sea válido
    3. Busca al usuario en la base de datos
    4. Devuelve el usuario
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(401, "Usuario no encontrado")

    return usuario
```

**Sin la dependencia:**

```python
@router.get("/me")
def mi_perfil(authorization: str = Header(None), db: Session = Depends(get_db)):
    # ❌ Código repetido en CADA endpoint
    if not authorization:
        raise HTTPException(401, "No autorizado")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Formato inválido")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY)
    except:
        raise HTTPException(401, "Token inválido")
    usuario = db.query(Usuario).filter(...).first()
    if not usuario:
        raise HTTPException(401, "Usuario no encontrado")
    return usuario
```

**Con la dependencia:**

```python
@router.get("/me")
def mi_perfil(current_user = Depends(get_current_user)):
    # ✅ Código limpio
    return current_user
```

### Dependencia de Rol

```python
def require_role(role_name: str):
    """Verifica que el usuario tenga un rol específico."""
    def role_checker(current_user = Depends(get_current_user)):
        roles = [rol.nombre for rol in current_user.roles]
        if role_name not in roles:
            raise HTTPException(403, f"Se requiere rol '{role_name}'")
        return True
    return role_checker

# Uso
@router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
def eliminar(id: int, db: Session = Depends(get_db)):
    # Solo administradores pueden eliminar
    eliminar_usuario(db, id)
```

---

## Response Model

### ¿Qué es `response_model`?

`response_model` le dice a FastAPI **qué datos devolver** y **qué datos ocultar**:

```python
@router.post("/", response_model=UsuarioResponse)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = crear_usuario(db, datos)
    return usuario
```

**Sin `response_model`:**

```python
# El modelo tiene estos campos:
class Usuario(Base):
    id_usuario: int
    nombre: str
    email: str
    password: str           # ❌ ¡No debería devolverse!
    contraseña_hash: str    # ❌ ¡Definitivamente no!
    created_at: datetime

# Si devuelves el modelo directamente:
return usuario
# El cliente recibe TODOS los campos, incluyendo contraseña_hash
```

**Con `response_model`:**

```python
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    created_at: datetime
    # Sin password ni contraseña_hash

@router.post("/", response_model=UsuarioResponse)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = crear_usuario(db, datos)
    return usuario
    # El cliente solo recibe: {id_usuario, nombre, email, created_at}
```

**Ventajas:**

1. **Seguridad:** Nunca devuelves campos sensibles
2. **Documentación:** Swagger muestra el schema correcto
3. **Validación:** Verifica que la respuesta sea correcta
4. **Conversión:** Convierte tipos automáticamente

---

## Documentación

### Swagger UI

FastAPI genera documentación automáticamente en `/docs`:

```
http://localhost:8000/docs
```

**Características:**

- Ver todos los endpoints
- Probar endpoints directamente
- Ver schemas de entrada y salida
- Autenticarse

### ReDoc

Otra versión de documentación en `/redoc`:

```
http://localhost:8000/redoc
```

**Diferencias:**

| Swagger UI | ReDoc |
|------------|-------|
| Interactivo (Try it out) | Solo lectura |
| Para probar | Para documentar |
| Organizado por tags | Organizado por modelo |

### Personalizar Documentación

```python
@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=201,
    summary="Crear un nuevo usuario",
    description="""
    Crea un nuevo usuario en el sistema.

    El email debe ser único. La contraseña debe tener al menos 6 caracteres.

    **Requisitos:**
    - Email válido
    - Contraseña de 6+ caracteres
    - Nombre de 2-100 caracteres
    """,
    responses={
        201: {"description": "Usuario creado exitosamente"},
        400: {"description": "Email ya registrado"},
        422: {"description": "Datos inválidos"}
    }
)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario."""
    return crear_usuario(db, datos)
```

---

## Ejemplo Completo

```python
# app/api/routers/usuarios.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user, require_role
from app.api.services.usuario_service import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    contar_usuarios
)
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario"
)
def crear(
    datos: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema.

    - **nombre**: Entre 2 y 100 caracteres
    - **email**: Debe ser único y válido
    - **password**: Mínimo 6 caracteres
    """
    try:
        return crear_usuario(db, datos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/",
    response_model=UsuarioListResponse,
    summary="Listar usuarios"
)
def listar(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos los usuarios con paginación."""
    usuarios = obtener_usuarios(db, skip=skip, limit=limit)
    total = contar_usuarios(db)
    return {"total": total, "usuarios": usuarios}

@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID"
)
def obtener(
    id_usuario: int = Path(..., gt=0, description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """Obtiene un usuario por su ID."""
    usuario = obtener_usuario_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario"
)
def actualizar(
    id_usuario: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualiza un usuario existente."""
    try:
        return actualizar_usuario(db, id_usuario, datos)
    except ValueError as e:
        if "no encontrado" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/{id_usuario}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    dependencies=[Depends(require_role("admin"))]
)
def eliminar(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    """Elimina un usuario. Requiere rol admin."""
    try:
        eliminar_usuario(db, id_usuario)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## Resumen

Aprendiste:

1. **Router** = El mesero que recibe pedidos HTTP
2. **Métodos HTTP** = GET (leer), POST (crear), PUT (reemplazar), DELETE (eliminar)
3. **Parámetros** = Path (en URL), Query (después de ?), Body (en cuerpo)
4. **Dependencias** = Cosas que FastAPI inyecta automáticamente
5. **Response model** = Filtra la respuesta (seguridad)
6. **Documentación** = Swagger UI y ReDoc generados automáticamente

**¿Listo para el siguiente paso?**

Ve a **07-autenticacion.md** para aprender cómo implementar login y seguridad.