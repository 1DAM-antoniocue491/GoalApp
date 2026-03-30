# Routers (API)

## Router

Un router agrupa endpoints relacionados bajo un mismo prefijo:

```
/api/v1/usuarios/     ← Router de usuarios
├── GET    /          ← Listar usuarios
├── POST   /          ← Crear usuario
├── GET    /{id}      ← Obtener usuario
├── PUT    /{id}      ← Actualizar usuario
└── DELETE /{id}      ← Eliminar usuario
```

> **¿Por qué usar routers en lugar de definir todo en main.py?**
>
> **Sin routers (todo en main.py):**
>
> ```python
> # main.py - se vuelve inmanejable
> @app.get("/api/v1/usuarios/")
> def listar_usuarios(): ...
>
> @app.post("/api/v1/usuarios/")
> def crear_usuario(): ...
>
> @app.get("/api/v1/ligas/")
> def listar_ligas(): ...
>
> @app.post("/api/v1/ligas/")
> def crear_liga(): ...
>
> # ... cientos de endpoints
> ```
>
> **Problemas:**
> - Un archivo con miles de líneas
> - Difícil de encontrar endpoints
> - Conflictos en equipos grandes
> - Sin organización lógica
>
> **Con routers:**
>
> ```python
> # routers/usuarios.py - Solo endpoints de usuarios
> router = APIRouter(prefix="/usuarios")
>
> @router.get("/")
> def listar(): ...
>
> @router.post("/")
> def crear(): ...
>
> # routers/ligas.py - Solo endpoints de ligas
> router = APIRouter(prefix="/ligas")
>
> # main.py - Registro
> app.include_router(usuarios.router, prefix="/api/v1")
> app.include_router(ligas.router, prefix="/api/v1")
> ```
>
> **Ventajas:**
> | Ventaja | Descripción |
> |---------|-------------|
> | **Organización** | Cada recurso en su archivo |
> | **Escalabilidad** | Fácil añadir nuevos routers |
> | **Colaboración** | Menos conflictos en Git |
> | **Reutilización** | Routers pueden importarse en múltiples apps |

## Estructura de un Router

```python
# app/api/routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.api.services.usuario_service import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario
)
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)
```

> **¿Qué significa cada parámetro de APIRouter?**
>
> | Parámetro | Propósito | Ejemplo |
> |-----------|----------|---------|
> | `prefix` | Prefijo para todos los endpoints del router | `/usuarios` |
> | `tags` | Etiquetas para agrupar en Swagger | `["Usuarios"]` |
>
> **Con `prefix="/usuarios"`:**
>
> ```python
> @router.get("/")        # GET /usuarios/
> @router.get("/{id}")   # GET /usuarios/{id}
> @router.post("/")      # POST /usuarios/
> ```
>
> **Sin prefix:**
>
> ```python
> @router.get("/")           # GET /
> @router.get("/usuarios/{id}")  # GET /usuarios/{id} (repetido)
> @router.post("/usuarios")     # POST /usuarios (repetido)
> ```
>
> **¿Por qué `tags`?**
>
> En Swagger UI (`/docs`), los endpoints se agrupan por tags:
>
> ```
> 📁 Usuarios
>   GET  /usuarios/
>   POST /usuarios/
>   GET  /usuarios/{id}
>
> 📁 Ligas
>   GET  /ligas/
>   POST /ligas/
> ```
>
> Sin tags, todos los endpoints aparecen desordenados.

## Endpoints REST

### Crear (POST)

```python
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
    """Crea un nuevo usuario en el sistema."""
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

> **¿Por qué cada decorador y parámetro?**
>
> **`@router.post("/")`**
>
> Define método HTTP y ruta. POST se usa para **crear** recursos.
>
> ```python
> # POST para crear
> @router.post("/")  # Crear recurso
> @router.put("/{id}")  # Actualizar recurso existente
> @router.patch("/{id}")  # Actualizar parcialmente
> @router.get("/")  # Listar recursos
> @router.delete("/{id}")  # Eliminar recurso
> ```
>
> **`response_model=UsuarioResponse`**
>
> Define qué campos devuelve la respuesta. Importante para seguridad:
>
> ```python
> # Sin response_model
> return usuario  # Devuelve TODOS los campos, incluyendo contraseña_hash
>
> # Con response_model
> return usuario  # Solo campos de UsuarioResponse (sin contraseña_hash)
> ```
>
> **`status_code=status.HTTP_201_CREATED`**
>
> Código de estado HTTP. 201 indica que se creó un recurso.
>
> | Código | Cuándo usar |
> |--------|-------------|
> | 200 | Operación exitosa genérica |
> | 201 | Recurso creado (POST) |
> | 204 | Sin contenido (DELETE) |
>
> **`summary="Crear un nuevo usuario"`**
>
> Texto corto que aparece en Swagger junto al endpoint.
>
> **`def crear(...)`**
>
> El nombre de la función se usa en OpenAPI. Debe ser descriptivo.

> **¿Por qué `try/except` con `ValueError`?**
>
> ```python
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     try:
>         return crear_usuario(db, datos)
>     except ValueError as e:
>         raise HTTPException(status_code=400, detail=str(e))
> ```
>
> **El flujo es:**
>
> 1. Servicio lanza `ValueError` para errores de negocio
> 2. Router captura `ValueError` y lo convierte a `HTTPException`
> 3. FastAPI convierte `HTTPException` a respuesta JSON con código HTTP
>
> **¿Por qué no lanzar `HTTPException` directamente en el servicio?**
>
> ```python
> # ❌ Servicio con HTTPException
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     if db.query(Usuario).filter(Usuario.email == datos.email).first():
>         raise HTTPException(400, "Email ya registrado")  # Conoce HTTP
> ```
>
> **Problema:** El servicio está acoplado a FastAPI/HTTP. No se puede reutilizar en:
> - Scripts CLI
> - Tests unitarios
> - Workers de fondo
>
> ```python
> # ✅ Servicio con excepciones genéricas
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     if db.query(Usuario).filter(Usuario.email == datos.email).first():
>         raise ValueError("Email ya registrado")  # No conoce HTTP
>
> # ✅ Router traduce a HTTP
> @router.post("/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     try:
>         return crear_usuario(db, datos)
>     except ValueError as e:
>         raise HTTPException(400, str(e))
> ```

### Listar (GET)

```python
@router.get(
    "/",
    response_model=List[UsuarioResponse],
    summary="Listar usuarios"
)
def listar(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene una lista de usuarios con paginación."""
    return obtener_usuarios(db, skip=skip, limit=limit)
```

> **¿Por qué paginación con `skip` y `limit`?**
>
> **Sin paginación:**
>
> ```python
> @router.get("/")
> def listar():
>     return db.query(Usuario).all()  # ¡Devuelve TODOS los usuarios!
> ```
>
> **Problemas:**
> - Si hay 1,000,000 de usuarios, la respuesta sería de cientos de MB
> - Tiempo de respuesta muy lento
> - Agotamiento de memoria en el servidor
>
> **Con paginación:**
>
> ```python
> @router.get("/")
> def listar(skip: int = 0, limit: int = 100):
>     return db.query(Usuario).offset(skip).limit(limit).all()
> ```
>
> | Petición | Resultado |
> |----------|-----------|
> | GET /usuarios?skip=0&limit=100 | Usuarios 1-100 |
> | GET /usuarios?skip=100&limit=100 | Usuarios 101-200 |
> | GET /usuarios?skip=0&limit=10 | Usuarios 1-10 |
>
> **¿Por qué `limit=100` por defecto?**
>
> - Previene respuestas gigantes
> - Permite al cliente obtener más si necesita
> - Balance entre flexibilidad y rendimiento
>
> **¿Por qué `response_model=List[UsuarioResponse]`?**
>
> ```python
> # Sin List[...]
> response_model=UsuarioResponse  # Espera un solo usuario
>
> # Con List[...]
> response_model=List[UsuarioResponse]  # Espera una lista de usuarios
> ```
>
> El schema define la estructura de cada elemento de la lista.

### Obtener por ID (GET)

```python
@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID"
)
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

> **¿Por qué usar `{id_usuario}` y no `{id}`?**
>
> ```python
> # ❌ Ambiguo
> @router.get("/{id}")
> def obtener(id: int):  # ¿id de qué?
>
> # ✅ Claro
> @router.get("/{id_usuario}")
> def obtener(id_usuario: int):  # Claro que es ID de usuario
> ```
>
> **Ventajas:**
> - Autodocumentación
> - En Swagger se ve claramente qué es
> - En logs, el parámetro es descriptivo

> **¿Por qué verificar `if not usuario`?**
>
> ```python
> usuario = obtener_usuario_por_id(db, id_usuario)
> if not usuario:
>     raise HTTPException(status_code=404, detail="Usuario no encontrado")
> ```
>
> **Sin verificación:**
>
> ```python
> usuario = obtener_usuario_por_id(db, 999)  # No existe
> return usuario  # Devuelve None
> # Respuesta: null con código 200 OK
> ```
>
> **Con verificación:**
>
> ```python
> usuario = obtener_usuario_por_id(db, 999)  # No existe
> if not usuario:
>     raise HTTPException(404, "Usuario no encontrado")
> # Respuesta: {"detail": "Usuario no encontrado"} con código 404
> ```
>
> **Códigos HTTP correctos:**
> - 200 OK: Recurso encontrado
> - 404 Not Found: Recurso no existe
> - Nunca 200 con `null`

### Actualizar (PUT)

```python
@router.put(
    "/{id_usuario}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario"
)
def actualizar(
    id_usuario: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un usuario existente."""
    try:
        usuario = actualizar_usuario(db, id_usuario, datos)
        return usuario
    except ValueError as e:
        if "no encontrado" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

> **¿Por qué PUT y no PATCH?**
>
> | Método | Semántica | Body |
> |--------|-----------|------|
> | PUT | Reemplazar recurso completo | Todos los campos |
> | PATCH | Actualizar parcialmente | Solo campos a cambiar |
>
> ```python
> # PUT - Reemplazo completo
> @router.put("/{id}")
> def actualizar(id: int, datos: UsuarioUpdate):
>     # Reemplaza TODO el usuario con los datos proporcionados
>     # Campos no enviados quedan como estaban
>
> # PATCH - Actualización parcial
> @router.patch("/{id}")
> def actualizar_parcial(id: int, datos: UsuarioPatch):
>     # Solo actualiza los campos enviados
>     # El resto se mantiene igual
> ```
>
> **En este proyecto usamos PUT para actualización completa:**
>
> ```python
> class UsuarioUpdate(BaseModel):
>     nombre: str | None = None      # Todos opcionales
>     email: EmailStr | None = None
>     telefono: str | None = None
> ```
>
> Si todos los campos son opcionales, PUT funciona como PATCH.

> **¿Por qué distinguir errores 404 de 400?**
>
> ```python
> except ValueError as e:
>     if "no encontrado" in str(e):
>         raise HTTPException(status_code=404, detail=str(e))
>     raise HTTPException(status_code=400, detail=str(e))
> ```
>
> | Código | Cuándo usar | Ejemplo |
> |--------|-------------|---------|
> | 404 | Recurso no existe | Usuario con ID 999 no existe |
> | 400 | Datos inválidos | Email ya registrado |
>
> **¿Por qué no usar `status_code=404` directamente en el servicio?**
>
> El servicio no debe conocer HTTP. Lanza `ValueError` con mensaje descriptivo, y el router decide el código HTTP basándose en el mensaje.

### Eliminar (DELETE)

```python
@router.delete(
    "/{id_usuario}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario"
)
def eliminar(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    """Elimina un usuario del sistema."""
    try:
        eliminar_usuario(db, id_usuario)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

> **¿Por qué `status_code=204` y no `200`?**
>
> | Código | Cuándo usar | Body |
> |--------|-------------|------|
> | 200 OK | Operación exitosa con body | Devuelve datos |
> | 204 No Content | Operación exitosa sin body | Sin body |
>
> ```python
> # Con 200 OK
> @router.delete("/{id}", status_code=200)
> def eliminar(id: int):
>     eliminar_usuario(db, id)
>     return {"mensaje": "Usuario eliminado"}  # Body innecesario
>
> # Con 204 No Content
> @router.delete("/{id}", status_code=204)
> def eliminar(id: int):
>     eliminar_usuario(db, id)
>     # Sin return - no hay body
> ```
>
> **204 es más semántico:** El cliente sabe que la operación fue exitosa y no hay contenido de respuesta.

> **¿Por qué no devolver el usuario eliminado?**
>
> ```python
> # ❌ Devolver usuario eliminado
> @router.delete("/{id}")
> def eliminar(id: int):
>     usuario = obtener_usuario(id)
>     eliminar_usuario(id)
>     return usuario  # Confuso: ¿para qué lo devuelvo si ya no existe?
>
> # ✅ Sin body
> @router.delete("/{id}", status_code=204)
> def eliminar(id: int):
>     eliminar_usuario(id)
>     # El 204 indica éxito, no necesita body
> ```

## Parámetros

### Path Parameters

```python
@router.get("/{id_usuario}")
def obtener(id_usuario: int):
    # id_usuario viene de la URL: /usuarios/123
    pass
```

> **¿Qué son los Path Parameters?**
>
> Valores que forman parte de la URL. Son obligatorios y se usan para identificar recursos.
>
> ```
> GET /usuarios/123          → id_usuario = 123
> GET /usuarios/abc          → Error: abc no es int
> GET /usuarios/             → Error: falta id_usuario
> GET /usuarios?id_usuario=1  → Error: id_usuario debe estar en el path
> ```
>
> **FastAPI valida automáticamente:**
> - Tipo de dato (`int`, `str`, etc.)
> - Conversión automática ("123" → 123)
> - Error 422 si el tipo es incorrecto

### Query Parameters

```python
@router.get("/")
def listar(
    skip: int = 0,              # Obligatorio si no tiene valor por defecto
    limit: int = 100,           # Opcional si tiene valor por defecto
    nombre: str | None = None,  # Opcional si puede ser None
    db: Session = Depends(get_db)
):
    # URL: /usuarios?skip=0&limit=10&nombre=Juan
    pass
```

> **¿Qué son los Query Parameters?**
>
> Parámetros opcionales que van después de `?` en la URL. Se usan para filtrar, ordenar, paginar.
>
> ```
> GET /usuarios                           → skip=0, limit=100, nombre=None
> GET /usuarios?limit=10                  → skip=0, limit=10, nombre=None
> GET /usuarios?skip=20&limit=10          → skip=20, limit=10, nombre=None
> GET /usuarios?nombre=Juan              → skip=0, limit=100, nombre="Juan"
> GET /usuarios?skip=0&limit=10&nombre=Juan → todos los parámetros
> ```
>
> **Obligatorio vs Opcional:**
>
> ```python
> # Obligatorio
> @router.get("/")
> def listar(orden: str):  # Sin valor por defecto = obligatorio
>     # GET /usuarios → Error: missing parameter 'orden'
>     # GET /usuarios?orden=asc → orden="asc"
>
> # Opcional con valor por defecto
> @router.get("/")
> def listar(skip: int = 0):  # Con valor por defecto = opcional
>     # GET /usuarios → skip=0
>     # GET /usuarios?skip=10 → skip=10
>
> # Opcional con None
> @router.get("/")
> def listar(nombre: str | None = None):
>     # GET /usuarios → nombre=None
>     # GET /usuarios?nombre=Juan → nombre="Juan"
> ```

### Body

```python
@router.post("/")
def crear(datos: UsuarioCreate):
    # datos se valida automáticamente con Pydantic
    pass
```

> **¿Qué es el Body?**
>
> Datos enviados en el cuerpo de la petición HTTP. Se usa para POST y PUT.
>
> ```
> POST /usuarios
> Content-Type: application/json
>
> {
>     "nombre": "Juan García",
>     "email": "juan@email.com",
>     "password": "mi_contraseña"
> }
> ```
>
> **Validación automática:**
>
> ```python
> class UsuarioCreate(BaseModel):
>     nombre: str = Field(..., min_length=2, max_length=100)
>     email: EmailStr
>     password: str = Field(..., min_length=6)
>
> @router.post("/")
> def crear(datos: UsuarioCreate):  # FastAPI valida automáticamente
>     # Si los datos no cumplen el schema, devuelve 422
>     # datos ya está validado y tipado
> ```

### Validación de parámetros

```python
from fastapi import Query, Path

@router.get("/{id_usuario}")
def obtener(
    id_usuario: int = Path(..., gt=0, description="ID del usuario")
):
    pass

@router.get("/")
def listar(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros")
):
    pass
```

> **¿Por qué usar `Path` y `Query`?**
>
> Sin ellos, solo puedes especificar el tipo y valor por defecto. Con ellos, puedes añadir validaciones y documentación.
>
> **Validaciones disponibles:**
>
> | Validación | Significado |
> |------------|-------------|
> | `gt=n` | Mayor que n |
> | `ge=n` | Mayor o igual que n |
> | `lt=n` | Menor que n |
> | `le=n` | Menor o igual que n |
> | `min_length=n` | Longitud mínima |
> | `max_length=n` | Longitud máxima |
> | `regex=r"..."` | Expresión regular |
>
> **Ejemplos:**
>
> ```python
> # ID debe ser mayor que 0
> id_usuario: int = Path(..., gt=0)
> # GET /usuarios/0 → Error 422
> # GET /usuarios/-1 → Error 422
> # GET /usuarios/1 → OK
>
> # Límite entre 1 y 1000
> limit: int = Query(100, ge=1, le=1000)
> # GET /usuarios?limit=0 → Error 422
> # GET /usuarios?limit=1001 → Error 422
> # GET /usuarios?limit=100 → OK
> ```

## Dependencias

### Base de datos

```python
# app/api/dependencies.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Uso
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).all()
```

> **¿Cómo funciona `Depends(get_db)`?**
>
> **Sin Depends (manual):**
>
> ```python
> @router.get("/")
> def listar():
>     db = SessionLocal()  # Crear sesión manualmente
>     try:
>         usuarios = db.query(Usuario).all()
>         return usuarios
>     finally:
>         db.close()  # ¡No olvidar cerrar!
> ```
>
> **Problemas:**
> - Código repetitivo
> - Fácil olvidar cerrar la sesión
> - Difícil de testear (no se puede mockear fácilmente)
>
> **Con Depends:**
>
> ```python
> @router.get("/")
> def listar(db: Session = Depends(get_db)):
>     return db.query(Usuario).all()
>     # db.close() se ejecuta automáticamente
> ```
>
> **El flujo:**
>
> 1. FastAPI llama a `get_db()`
> 2. `get_db()` crea la sesión: `db = SessionLocal()`
> 3. `yield db` proporciona la sesión al endpoint
> 4. El endpoint ejecuta su código
> 5. `finally: db.close()` se ejecuta siempre

> **¿Por qué `yield` y no `return`?**
>
> ```python
> # ❌ Con return - db.close() NUNCA se ejecuta
> def get_db():
>     db = SessionLocal()
>     return db  # Retorna inmediatamente
>     db.close()  # ¡Código inalcanzable!
>
> # ✅ Con yield - db.close() se ejecuta después del endpoint
> def get_db():
>     db = SessionLocal()
>     try:
>         yield db  # Proporciona db, PAUSA aquí
>     finally:
>         db.close()  # Se ejecuta DESPUÉS del endpoint
> ```

### Usuario autenticado

```python
# app/api/dependencies.py
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(401, "Usuario no encontrado")
    return usuario

# Uso
@router.get("/me")
def mi_perfil(current_user = Depends(get_current_user)):
    return current_user
```

> **¿Cómo funciona OAuth2PasswordBearer?**
>
> ```python
> oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
> ```
>
> Este dependencia:
> 1. Busca el header `Authorization: Bearer <token>` en la petición
> 2. Extrae el token
> 3. Si no hay token, devuelve 401 automáticamente
> 4. Proporciona el token como string
>
> **Sin OAuth2PasswordBearer:**
>
> ```python
> @router.get("/me")
> def mi_perfil(authorization: str = Header(None)):
>     if not authorization:
>         raise HTTPException(401, "No autorizado")
>     if not authorization.startswith("Bearer "):
>         raise HTTPException(401, "Formato inválido")
>     token = authorization.replace("Bearer ", "")
>     # Validar token...
> ```
>
> **Con OAuth2PasswordBearer:**
>
> ```python
> @router.get("/me")
> def mi_perfil(token: str = Depends(oauth2_scheme)):
>     # token ya está extraído del header
>     # Si no hay token, ya devolvió 401
> ```

> **¿Por qué anidar dependencias?**
>
> ```python
> def get_current_user(
>     token: str = Depends(oauth2_scheme),  # Dependencia 1
>     db: Session = Depends(get_db)         # Dependencia 2
> ):
> ```
>
> FastAPI ejecuta las dependencias en orden:
>
> 1. `oauth2_scheme` extrae el token del header
> 2. `get_db` crea la sesión de BD
> 3. `get_current_user` usa ambos para validar y obtener el usuario
>
> **En el endpoint:**
>
> ```python
> @router.get("/me")
> def mi_perfil(current_user = Depends(get_current_user)):
>     # current_user ya está autenticado
>     # Si el token es inválido, ya se devolvió 401
>     # Si el usuario no existe, ya se devolvió 401
>     return current_user
> ```

### Verificar rol

```python
def require_role(role_name: str):
    def role_checker(current_user = Depends(get_current_user)):
        roles = [rol.nombre for rol in current_user.roles]
        if role_name not in roles:
            raise HTTPException(403, f"Se requiere rol '{role_name}'")
        return True
    return role_checker

# Uso
@router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
def eliminar(id: int, db: Session = Depends(get_db)):
    pass
```

> **¿Por qué una función que devuelve una función?**
>
> **Problema:** Necesitamos pasar el nombre del rol como parámetro.
>
> ```python
> # ❌ Esto no funciona porque Depends espera una función, no un valor
> @router.delete("/{id}", dependencies=[Depends(require_role)])  # ¿Cómo pasamos "admin"?
> ```
>
> **Solución:** Una fábrica de dependencias.
>
> ```python
> def require_role(role_name: str):  # Recibe "admin"
>     def role_checker(current_user = Depends(get_current_user)):  # Esta es la dependencia real
>         roles = [rol.nombre for rol in current_user.roles]
>         if role_name not in roles:  # Usa el parámetro del closure
>             raise HTTPException(403, f"Se requiere rol '{role_name}'")
>         return True
>     return role_checker  # Devuelve la función que FastAPI ejecutará
>
> # Uso
> @router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
> # require_role("admin") devuelve role_checker
> # FastAPI ejecuta role_checker(current_user)
> ```

> **¿Por qué `dependencies` en lugar de parámetro?**
>
> ```python
> # Opción 1: dependencies=[] - No necesitamos el resultado
> @router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
> def eliminar(id: int, db: Session = Depends(get_db)):
>     # Si no tiene rol admin, ya devolvió 403
>     # No necesitamos el resultado de require_role
>
> # Opción 2: Parámetro - Si necesitamos el resultado
> @router.delete("/{id}")
> def eliminar(
>     id: int,
>     db: Session = Depends(get_db),
>     _ = Depends(require_role("admin"))  # _ indica que no usamos el valor
> ):
>     pass
> ```

## Documentación

### Swagger UI

Disponible en: `http://localhost:8000/docs`

> **¿Qué es Swagger UI?**
>
> Una interfaz interactiva para probar la API directamente desde el navegador:
>
> - Ver todos los endpoints organizados por tags
> - Ver schemas de entrada y salida
> - Probar endpoints con el botón "Try it out"
> - Ver respuestas y códigos de estado
> - Autenticarse con Bearer token
>
> **Generado automáticamente por FastAPI:**
>
> FastAPI analiza:
> - Tipos de parámetros (path, query, body)
> - Schemas Pydantic
> - Response models
> - Status codes
> - Docstrings

### ReDoc

Disponible en: `http://localhost:8000/redoc`

> **Diferencias entre Swagger UI y ReDoc:**
>
> | Swagger UI | ReDoc |
> |------------|-------|
> | Interactivo (Try it out) | Solo lectura |
> | Para desarrolladores | Para documentación |
> | Tests rápidos | Visión general |
> | Organizado por tags | Organizado por modelo |
>
> **Usar Swagger UI para:**
> - Probar endpoints durante desarrollo
> - Debugging
> - Tests manuales
>
> **Usar ReDoc para:**
> - Documentación oficial del API
> - Compartir con equipos frontend
> - Referencia rápida de modelos

### Personalizar documentación

```python
@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=201,
    summary="Crear usuario",
    description="Registra un nuevo usuario en el sistema",
    responses={
        201: {"description": "Usuario creado"},
        400: {"description": "Email ya registrado"},
        422: {"description": "Datos inválidos"}
    }
)
def crear(datos: UsuarioCreate):
    pass
```

> **¿Por qué personalizar la documentación?**
>
> **Sin personalización:**
>
> Swagger muestra información genérica:
> - "POST /usuarios/"
> - "Response: UsuarioResponse"
> - Sin ejemplos
> - Sin descripción
>
> **Con personalización:**
>
> - Summary: Título claro del endpoint
> - description: Explicación detallada
> - responses: Documenta cada código de error
> - response_model: Schema de respuesta
>
> **Ejemplo completo:**
>
> ```python
> @router.post(
>     "/",
>     response_model=UsuarioResponse,
>     status_code=status.HTTP_201_CREATED,
>     summary="Crear un nuevo usuario",
>     description="""
>     Registra un nuevo usuario en el sistema.
>
>     El email debe ser único en el sistema.
>     La contraseña debe tener al menos 6 caracteres.
>
>     **Requisitos:**
>     - Email válido
>     - Contraseña de 6+ caracteres
>     - Nombre de 2-100 caracteres
>     """,
>     responses={
>         201: {
>             "description": "Usuario creado exitosamente",
>             "content": {
>                 "application/json": {
>                     "example": {
>                         "id_usuario": 1,
>                         "nombre": "Juan García",
>                         "email": "juan@email.com"
>                     }
>                 }
>             }
>         },
>         400: {
>             "description": "El email ya está registrado",
>             "content": {
>                 "application/json": {
>                     "example": {"detail": "El email ya está registrado"}
>                 }
>             }
>         }
>     }
> )
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     ...
> ```

## Registro de Routers

```python
# app/main.py
from app.api.routers import usuarios, ligas, auth

app = FastAPI(title="Liga Amateur App")

app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(ligas.router, prefix="/api/v1", tags=["Ligas"])
```

> **¿Por qué `include_router` en lugar de definir routers en main.py?**
>
> **Sin include_router:**
>
> ```python
> # main.py
> @app.get("/api/v1/usuarios/")
> def listar(): ...
>
> @app.post("/api/v1/usuarios/")
> def crear(): ...
>
> # Todo en un archivo, difícil de mantener
> ```
>
> **Con include_router:**
>
> ```python
> # main.py - Solo registro
> app.include_router(usuarios.router, prefix="/api/v1")
>
> # routers/usuarios.py - Toda la lógica de usuarios
> router = APIRouter(prefix="/usuarios")
> @router.get("/")
> def listar(): ...
> ```
>
> **Prefijo combinado:**
>
> ```python
> # En el router
> router = APIRouter(prefix="/usuarios")
>
> # En main.py
> app.include_router(router, prefix="/api/v1")
>
> # Resultado: /api/v1/usuarios/
> ```

## Ejemplo Completo

```python
# app/api/routers/ligas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user, require_role
from app.api.services.liga_service import (
    crear_liga,
    obtener_ligas,
    obtener_liga_por_id,
    actualizar_liga,
    eliminar_liga
)
from app.schemas.liga import LigaCreate, LigaUpdate, LigaResponse

router = APIRouter(prefix="/ligas", tags=["Ligas"])

@router.post(
    "/",
    response_model=LigaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))]
)
def crear(datos: LigaCreate, db: Session = Depends(get_db)):
    """Crea una nueva liga. Requiere rol admin."""
    return crear_liga(db, datos)

@router.get("/", response_model=List[LigaResponse])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas las ligas."""
    return obtener_ligas(db, skip, limit)

@router.get("/{id_liga}", response_model=LigaResponse)
def obtener(id_liga: int, db: Session = Depends(get_db)):
    """Obtiene una liga por su ID."""
    liga = obtener_liga_por_id(db, id_liga)
    if not liga:
        raise HTTPException(404, "Liga no encontrada")
    return liga

@router.put("/{id_liga}", response_model=LigaResponse, dependencies=[Depends(require_role("admin"))])
def actualizar(id_liga: int, datos: LigaUpdate, db: Session = Depends(get_db)):
    """Actualiza una liga. Requiere rol admin."""
    return actualizar_liga(db, id_liga, datos)

@router.delete("/{id_liga}", status_code=204, dependencies=[Depends(require_role("admin"))])
def eliminar(id_liga: int, db: Session = Depends(get_db)):
    """Elimina una liga. Requiere rol admin."""
    eliminar_liga(db, id_liga)
```

> **Resumen del patrón usado:**
>
> | Elemento | Propósito |
> |----------|-----------|
> | `APIRouter(prefix="/ligas")` | Agrupa endpoints bajo `/ligas` |
> | `tags=["Ligas"]` | Agrupa en Swagger |
> | `response_model=LigaResponse` | Filtra respuesta |
> | `status_code=201` | Código HTTP para creación |
> | `dependencies=[Depends(require_role("admin"))]` | Protege endpoint |
> | `db: Session = Depends(get_db)` | Inyecta BD |
> | `try/except ValueError` | Maneja errores del servicio |
> | `HTTPException(404)` | Error de recurso no encontrado |
> | `HTTPException(400)` | Error de validación |