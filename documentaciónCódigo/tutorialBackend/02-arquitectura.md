# Arquitectura del Proyecto

## Arquitectura en Capas

El backend sigue una arquitectura en capas donde cada capa tiene una responsabilidad específica:

```
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                 │
│                    (Routers / Endpoints)                │
├─────────────────────────────────────────────────────────┤
│                    CAPA DE LÓGICA                       │
│                    (Services)                           │
├─────────────────────────────────────────────────────────┤
│                    CAPA DE DATOS                        │
│                    (Models / ORM)                       │
├─────────────────────────────────────────────────────────┤
│                    BASE DE DATOS                        │
│                    (MySQL)                              │
└─────────────────────────────────────────────────────────┘
```

**¿Por qué usar arquitectura en capas?**

La arquitectura en capas es un patrón de diseño que **separa responsabilidades** en niveles distintos. Cada capa solo conoce la capa inmediatamente inferior.

**Ventajas:**

1. **Separación de responsabilidades**: Cada capa tiene un trabajo específico y no se mezcla con otros.

2. **Mantenibilidad**: Si necesitas cambiar la base de datos de MySQL a PostgreSQL, solo modificas la capa de datos. El resto del código permanece igual.

3. **Testabilidad**: Puedes probar cada capa de forma aislada. Por ejemplo, probar la lógica de negocio sin necesidad de una base de datos real.

4. **Reutilización**: El mismo servicio puede ser usado por diferentes routers (API REST, GraphQL, CLI).

**Flujo de datos:**

```
Petición HTTP → Router (valida) → Service (lógica) → Model (ORM) → Base de datos
                                   ↓
                             Router (formatea) → Respuesta HTTP
```

**Regla de oro**: Los routers nunca acceden directamente a los modelos. Siempre pasan por los servicios.

## Estructura de Carpetas

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada, configuración FastAPI
│   ├── config.py                # Variables de entorno (Pydantic Settings)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Dependencias inyectables (get_db, auth)
│   │   ├── routers/             # Endpoints HTTP
│   │   │   ├── auth.py          # Autenticación
│   │   │   ├── usuarios.py      # CRUD usuarios
│   │   │   ├── ligas.py         # CRUD ligas
│   │   │   └── ...
│   │   │
│   │   └── services/             # Lógica de negocio
│   │       ├── usuario_service.py
│   │       ├── liga_service.py
│   │       └── ...
│   │
│   ├── models/                   # Modelos ORM (tablas)
│   │   ├── usuario.py
│   │   ├── liga.py
│   │   └── ...
│   │
│   ├── schemas/                 # Validación (Pydantic)
│   │   ├── usuario.py
│   │   ├── liga.py
│   │   └── ...
│   │
│   └── database/
│       ├── connection.py        # Engine, SessionLocal, Base
│       └── init.sql             # Script SQL inicial
│
├── .env
├── requirements.txt
└── README.md
```

**¿Por qué esta estructura de carpetas?**

**Organización por tipo de componente:**

- `routers/`: Agrupa todos los endpoints. Facilita encontrar "¿dónde está el endpoint de usuarios?".
- `services/`: Toda la lógica de negocio en un lugar.
- `models/`: Definición de tablas.
- `schemas/`: Contratos de entrada/salida de la API.

**Alternativa: Organización por dominio (vertical slice)**

```
backend/
└── app/
    ├── usuarios/
    │   ├── router.py
    │   ├── service.py
    │   ├── model.py
    │   └── schemas.py
    └── ligas/
        └── ...
```

**¿Cuándo usar cada enfoque?**

| Enfoque | Mejor para | Pros | Contras |
|---------|-----------|------|---------|
| Por tipo | Proyectos pequeños/medianos | Fácil de entender para nuevos devs | Archivos relacionados están dispersos |
| Por dominio | Proyectos grandes/microservicios | Todo lo de "usuarios" junto | Requiere más estructura inicial |

**Para este proyecto**: Elegimos organización por tipo porque:
- Es más fácil de entender para nuevos desarrolladores
- El proyecto no es muy grande
- Facilita ver "todos los routers" o "todos los modelos" de un vistazo

## Responsabilidades por Componente

### `main.py` - Punto de Entrada

```python
from fastapi import FastAPI
from .config import settings
from .database.connection import engine, Base
from .api.routers import auth, usuarios, ligas

# Eventos del ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Registrar routers
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(ligas.router, prefix="/api/v1", tags=["Ligas"])
```

**¿Por qué usar `lifespan` en lugar de eventos `on_startup`/`on_shutdown`?**

**Forma antigua (deprecated):**

```python
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    engine.dispose()
```

**Forma moderna (recomendada):**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    engine.dispose()
```

**Ventajas del `lifespan`:**

1. **Código relacionado junto**: Startup y shutdown están en el mismo lugar.

2. **Manejo de recursos async**: Funciona correctamente con conexiones asíncronas.

3. **Contexto gestionado**: Los recursos creados en startup se limpian automáticamente si hay error.

4. **Testing más fácil**: Puedes simular el ciclo de vida completo en tests.

**Responsabilidades:**
- Crear la instancia de FastAPI
- Configurar middleware (CORS)
- Registrar todos los routers
- Gestionar eventos de inicio/parada

**¿Por qué registrar routers con `include_router`?**

```python
# ❌ Todo en un archivo - difícil de mantener
@app.get("/usuarios/")
def listar_usuarios(): ...

@app.post("/usuarios/")
def crear_usuario(): ...

@app.get("/ligas/")
def listar_ligas(): ...
# ...cientos de endpoints

# ✅ Routers separados - organizado
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(ligas.router, prefix="/api/v1", tags=["Ligas"])
```

**Ventajas:**

1. **Separación**: Cada recurso tiene su archivo.
2. **Prefijo común**: `/api/v1` para todos los endpoints, fácil de cambiar.
3. **Tags automáticos**: Documentación Swagger agrupada por tags.
4. **Reutilización**: Un router puede incluirse en múltiples apps.

### `config.py` - Configuración

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    APP_NAME: str = "Liga Amateur App"

    model_config = {"env_file": ".env"}

settings = Settings()
```

**¿Por qué una clase `Settings` en lugar de variables globales?**

**Forma problemática:**

```python
# config.py
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///default.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-key")
# Problema: no hay validación, tipos incorrectos silenciosos
```

**Forma recomendada:**

```python
class Settings(BaseSettings):
    DATABASE_URL: str           # Obligatorio, error si falta
    SECRET_KEY: str             # Obligatorio
    APP_NAME: str = "Default"   # Opcional con valor por defecto
```

**Ventajas de la clase Settings:**

1. **Validación al inicio**: Si falta `DATABASE_URL`, la aplicación falla inmediatamente al arrancar, no en medio de una petición.

2. **Tipado**: `PORT` es `int`, no `str`. Conversión automática.

3. **Integración con IDE**: Autocompletado disponible.

4. **Singleton**: `settings = Settings()` una vez, usado en todo el proyecto.

5. **Testing fácil**: Puedes crear instancias con valores diferentes para tests.

**Responsabilidades:**
- Centralizar configuración
- Leer variables de entorno
- Validar tipos de datos

### `models/` - Modelos ORM

Representan tablas de la base de datos como clases Python:

```python
from sqlalchemy import Column, Integer, String, DateTime
from ..database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # Clave primaria
    id_usuario = Column(Integer, primary_key=True, index=True)

    # Campos obligatorios
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    contraseña_hash = Column(String(255), nullable=False)

    # Campos automáticos
    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")
```

**¿Por qué usar ORM en lugar de SQL directo?**

**Con SQL directo:**

```python
# Peligroso y propenso a errores
cursor.execute(f"SELECT * FROM usuarios WHERE id = {user_id}")  # Inyección SQL

# Verboso
cursor.execute(
    "INSERT INTO usuarios (nombre, email, contraseña_hash) VALUES (?, ?, ?)",
    (nombre, email, hash)
)
usuario_id = cursor.lastrowid
```

**Con ORM:**

```python
# Seguro y expresivo
usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

# Simple
usuario = Usuario(nombre=nombre, email=email, contraseña_hash=hash)
db.add(usuario)
db.commit()
db.refresh(usuario)  # Obtiene el ID generado
```

**Ventajas del ORM:**

| Ventaja | Descripción |
|---------|-------------|
| **Seguridad** | Prevención automática de inyección SQL |
| **Productividad** | Menos código, más legible |
| **Portabilidad** | Cambiar de MySQL a PostgreSQL solo cambiando `DATABASE_URL` |
| **Relaciones** | Navegación fácil: `usuario.roles` en lugar de JOINs manuales |
| **Migraciones** | Alembic detecta cambios automáticamente |

**Desventajas:**

| Desventaja | Mitigación |
|------------|------------|
| Overhead de abstracción | Usar SQL directo para queries complejas |
| Curva de aprendizaje | Documentación extensa |
| Debugging difícil | `echo=True` para ver SQL generado |

**Responsabilidades:**
- Definir estructura de tablas
- Mapear tipos SQL a tipos Python
- Definir relaciones entre tablas

### `schemas/` - Validación de Datos

Definen cómo entran y salen los datos de la API:

```python
from pydantic import BaseModel, EmailStr, Field

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
```

**¿Por qué separar schemas de models?**

**Problema si usamos el modelo directamente:**

```python
# El modelo Usuario tiene contraseña_hash
@router.get("/usuarios/{id}")
def obtener(id: int):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
    return usuario  # ¡Expone la contraseña!
```

**Con schemas separados:**

```python
# UsuarioResponse NO tiene contraseña
@router.get("/usuarios/{id}", response_model=UsuarioResponse)
def obtener(id: int):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
    return usuario  # Solo campos de UsuarioResponse
```

**Diferentes schemas para diferentes usos:**

| Schema | Uso | Campos |
|--------|-----|--------|
| `UsuarioCreate` | POST /usuarios/ | nombre, email, password |
| `UsuarioUpdate` | PUT /usuarios/{id} | nombre?, email? (opcionales) |
| `UsuarioResponse` | GET /usuarios/ | id, nombre, email, created_at |
| `UsuarioListResponse` | GET /usuarios/ | lista de UsuarioResponse |

**Ventajas de separar:**

1. **Seguridad**: Diferentes campos para entrada y salida.
2. **Validación**: EmailStr valida formato, min_length para contraseña.
3. **Documentación**: Swagger usa estos schemas automáticamente.
4. **Flexibilidad**: Puedes agregar campos calculados en Response (ej: `nombre_completo`).

**Responsabilidades:**
- Validar datos de entrada
- Definir formato de respuesta
- Documentar la API automáticamente

### `services/` - Lógica de Negocio

Contienen toda la lógica de la aplicación:

```python
def crear_usuario(db: Session, datos: UsuarioCreate):
    # Verificar email único
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hash_password(datos.password)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
```

**¿Por qué no poner la lógica en el router?**

**Lógica en router (anti-patrón):**

```python
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # Problema: lógica de negocio mezclada con HTTP
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(400, "Email ya registrado")

    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hash_password(datos.password)
    )
    db.add(usuario)
    db.commit()
    return usuario
```

**Lógica en servicio (patrón correcto):**

```python
# Router - solo HTTP
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(db, datos)
    except ValueError as e:
        raise HTTPException(400, str(e))

# Service - solo lógica
def crear_usuario(db: Session, datos: UsuarioCreate):
    # Regla de negocio: email único
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise ValueError("Email ya registrado")
    # Crear usuario...
```

**Ventajas de separar:**

1. **Reutilización**: El mismo servicio puede usarse desde REST API, CLI, o tests.

2. **Testing**: Probar lógica sin necesidad de peticiones HTTP.

3. **Single Responsibility**: Router maneja HTTP, Service maneja negocio.

4. **Mantenimiento**: Cambiar reglas de negocio en un solo lugar.

**Responsabilidades:**
- Consultar/modificar la base de datos
- Implementar reglas de negocio
- Manejar errores específicos

### `routers/` - Endpoints HTTP

Definen los endpoints y delegan a los servicios:

```python
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_db
from app.api.services.usuario_service import crear_usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**¿Qué hace exactamente el router?**

1. **Recibir petición HTTP**: El decorador `@router.post` define la ruta.

2. **Validar entrada**: Pydantic valida `datos` automáticamente.

3. **Inyectar dependencias**: `Depends(get_db)` proporciona la sesión de BD.

4. **Delegar al servicio**: Llama a `crear_usuario()`.

5. **Manejar errores**: Convierte `ValueError` a `HTTPException`.

6. **Formatear respuesta**: `response_model` filtra y serializa la respuesta.

**¿Por qué usar `response_model`?**

```python
# Sin response_model
@router.get("/usuarios/{id}")
def obtener(id: int, db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.id_usuario == id).first()
# Devuelve TODOS los campos del modelo, incluyendo contraseña_hash

# Con response_model
@router.get("/usuarios/{id}", response_model=UsuarioResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return db.query(Usuario).filter(Usuario.id_usuario == id).first()
# Solo devuelve los campos definidos en UsuarioResponse
```

**Responsabilidades:**
- Definir rutas HTTP
- Validar datos con schemas
- Delegar lógica a servicios
- Manejar errores HTTP

### `dependencies.py` - Inyección de Dependencias

```python
from app.database.connection import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Validar JWT y obtener usuario
    ...
    return usuario
```

**¿Qué es la Inyección de Dependencias?**

**Sin dependencias (problemático):**

```python
@router.get("/usuarios/me")
def mi_perfil():
    # Problema: ¿de dónde sale db? ¿token?
    db = SessionLocal()  # Acoplado, difícil de testear
    token = request.headers.get("Authorization")  # Manual
    ...
```

**Con dependencias (correcto):**

```python
@router.get("/usuarios/me")
def mi_perfil(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # db y user se inyectan automáticamente
    # Fácil de testear: solo pasamos mocks
    return user
```

**Ventajas:**

1. **Testeabilidad**: En tests, reemplazamos `get_db` con una base de datos en memoria.

2. **Ciclo de vida**: `get_db` garantiza que la sesión se cierra después de cada petición.

3. **Reutilización**: `get_current_user` se usa en todos los endpoints protegidos.

4. **Legibilidad**: Las dependencias están declaradas explícitamente en la firma.

**El patrón `yield`:**

```python
def get_db():
    db = SessionLocal()  # 1. Antes de yield: setup
    try:
        yield db         # 2. Durante yield: proporciona el recurso
    finally:
        db.close()       # 3. Después de yield: cleanup (SIEMPRE se ejecuta)
```

Esto garantiza que `db.close()` siempre se ejecuta, incluso si hay una excepción.

**Responsabilidades:**
- Proporcionar dependencias inyectables
- Gestionar ciclo de vida de conexiones
- Implementar autenticación

## Flujo de una Petición

```
┌─────────────────────────────────────────────────────────────────┐
│  POST /api/v1/usuarios                                          │
│  Body: {"nombre": "Juan", "email": "juan@email.com", ...}       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. ROUTER (usuarios.py)                                        │
│     - Recibe la petición HTTP                                    │
│     - Valida datos con UsuarioCreate schema                      │
│     - Inyecta dependencias (get_db)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. SERVICE (usuario_service.py)                                │
│     - Ejecuta lógica de negocio                                  │
│     - Verifica si el email ya existe                             │
│     - Hashea la contraseña                                       │
│     - Crea el objeto Usuario                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. MODEL (usuario.py - ORM)                                    │
│     - Mapea el objeto a fila SQL                                  │
│     - Ejecuta INSERT INTO usuarios (...)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. RESPONSE                                                     │
│     - Router convierte a UsuarioResponse                         │
│     - Retorna: {"id_usuario": 1, "nombre": "Juan", ...}          │
│     - Status: 201 Created                                         │
└─────────────────────────────────────────────────────────────────┘
```

**¿Por qué este flujo específico?**

**Alternativa: Router → Modelo directamente (anti-patrón)**

```
Router → Modelo → BD
```

Problema: Lógica de negocio (validar email único, hashear contraseña) se mezcla con HTTP.

**Flujo correcto: Router → Service → Modelo**

1. **Router**: Solo HTTP. Recibe petición, valida formato, devuelve respuesta.

2. **Service**: Solo lógica. Reglas de negocio, validaciones, transformaciones.

3. **Model**: Solo datos. Mapeo a tabla SQL.

**Ejemplo: Crear usuario**

| Capa | Responsabilidad | Código |
|------|----------------|--------|
| Router | Recibir POST, validar schema | `@router.post("/usuarios/")` |
| Service | Verificar email único, hashear contraseña | `crear_usuario(db, datos)` |
| Model | INSERT en BD | `db.add(usuario)` |

**Beneficio principal**: Si mañana necesitas crear usuarios desde una CLI o un script de migración, usas el mismo servicio sin tocar el router.

## Diagrama de Dependencias

```
main.py
    │
    ├── config.py (settings)
    │
    ├── database/connection.py (engine, SessionLocal)
    │
    └── api/routers/
            │
            ├── dependencies.py (get_db, get_current_user)
            │
            ├── schemas/ (validación)
            │
            └── services/
                    │
                    └── models/ (ORM)
```

**¿Por qué esta dirección de dependencias?**

**Regla de dependencias (Dependency Rule):**

- Las capas interiores **no conocen** las capas exteriores.
- Las capas exteriores **conocen** las capas interiores.

```
main.py → routers → services → models
  ↓         ↓         ↓         ↓
config   schemas   (ninguna)   connection
```

**¿Qué significa esto?**

- `models` **NO** importa de `services` o `routers`.
- `services` **puede** importar de `models`.
- `routers` **puede** importar de `services` y `models`.
- `main.py` **puede** importar de todo.

**¿Por qué importa?**

Si `models` importara de `services`, tendrías una **dependencia circular**:

```python
# models/usuario.py
from services.usuario_service import crear_usuario  # ❌ MAL

# services/usuario_service.py
from models.usuario import Usuario  # ✅ BIEN
```

**Problema de dependencia circular:**
1. Python no puede importar correctamente
2. Código difícil de entender y mantener
3. Testing se vuelve imposible

**Regla:** Los routers nunca acceden directamente a los modelos. Siempre pasan por los servicios.