# Arquitectura del Proyecto (Para Principiantes)

## ¿Qué es la Arquitectura?

Imagina que vas a construir una casa. No empiezas poniendo ladrillos al azar. Primero necesitas un **plano** que diga:

- Dónde va la cocina
- Dónde van los cuartos
- Dónde van los baños
- Cómo se conecta todo

La **arquitectura** de un software es igual: es el plano que dice **cómo se organiza el código**.

---

## La Arquitectura en Capas

### La Metáfora del Restaurante

Piensa en un restaurante. Tiene diferentes partes que trabajan juntas:

```
┌─────────────────────────────────────────────────────────┐
│                    MESEROS                              │
│              (Hablan con los clientes)                 │
│         "Hola, ¿qué desea ordenar?"                    │
├─────────────────────────────────────────────────────────┤
│                    COCINA                               │
│              (Preparan la comida)                       │
│         "Aquí está tu hamburguesa"                     │
├─────────────────────────────────────────────────────────┤
│                    DESPENSA                              │
│              (Organizan los ingredientes)               │
│         "El tomate está en la nevera"                  │
├─────────────────────────────────────────────────────────┤
│                    NEVERA                                │
│              (Guardan todo organizado)                  │
│         "Aquí guardamos la leche, los huevos..."       │
└─────────────────────────────────────────────────────────┘
```

### En Nuestro Proyecto

| Capa | En el Restaurante | En el Software | ¿Qué hace? |
|------|-------------------|-----------------|------------|
| **Presentación** | Meseros | Routers | Hablan con el cliente (reciben pedidos) |
| **Lógica** | Cocina | Services | Preparan la respuesta (reglas de negocio) |
| **Datos** | Despensa | Models | Organizan los ingredientes (tablas) |
| **Almacenamiento** | Nevera | Base de datos | Guardan todo (MySQL) |

### ¿Por qué separar en capas?

**Imagina un restaurante sin organización:**

```
❌ El mesero también cocina, limpia y cobra
❌ El cocinero también atiende mesas
❌ Nadie sabe qué hace cada quien
❌ Si algo falla, nadie sabe dónde está el problema
```

**Un restaurante organizado:**

```
✅ El mesero SOLO atiende al cliente
✅ El cocinero SOLO cocina
✅ Cada quien tiene su trabajo
✅ Si falla algo, sabemos quién es el responsable
```

---

## Cómo Fluye un Pedido

### Ejemplo: "Quiero ver todos los equipos"

```
📱 Cliente (Frontend)
   "GET /api/v1/equipos/"
   ↓

🚪 ROUTER (La recepcionista)
   "Hola, ¿qué necesitas? Ah, quieres equipos."
   Verifica que el pedido esté bien escrito.
   ↓

👨‍🍳 SERVICE (El chef)
   "Entendido. Voy a buscar los equipos."
   Aplica las reglas de negocio.
   ↓

📦 MODEL (El organizador de la nevera)
   "SQLAlchemy, traduce esto por favor."
   SELECT * FROM equipos
   ↓

🗄️ BASE DE DATOS (La nevera)
   "Aquí están los 10 equipos que guardé."
   ↓

📦 MODEL
   "Perfecto, los convertí a objetos Python."
   ↓

👨‍🍳 SERVICE
   "Listo, aquí están los equipos."
   ↓

🚪 ROUTER
   "Aquí tienes la respuesta:"
   [{"id": 1, "nombre": "Real Madrid"}, ...]
   ↓

📱 Cliente
   "¡Gracias! Ahora muestro los equipos en pantalla."
```

### ¿Por qué tantos pasos?

Cada paso tiene **una responsabilidad específica**:

| Paso | Responsabilidad | ¿Por qué separarlo? |
|------|-----------------|---------------------|
| Router | Validar el pedido | Si el formato está mal, falla aquí |
| Service | Reglas de negocio | Si la lógica está mal, falla aquí |
| Model | Organizar datos | Si la consulta está mal, falla aquí |
| Base de datos | Guardar datos | Si los datos están corruptos, falla aquí |

**Si algo falla, ¡sabes exactamente dónde buscar!**

---

## Estructura de Carpetas

### El Árbol de Carpetas

```
backend/
├── app/
│   ├── __init__.py           # Dice "esto es un paquete Python"
│   ├── main.py               # Donde inicia todo (el jefe)
│   ├── config.py             # Configuraciones (las reglas)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py   # Cosas que todos necesitan
│   │   ├── routers/          # Los meseros (endpoints)
│   │   │   ├── auth.py       # Mesero de autenticación
│   │   │   ├── usuarios.py   # Mesero de usuarios
│   │   │   ├── ligas.py      # Mesero de ligas
│   │   │   └── ...
│   │   │
│   │   └── services/         # La cocina (lógica de negocio)
│   │       ├── usuario_service.py
│   │       ├── liga_service.py
│   │       └── ...
│   │
│   ├── models/               # La despensa (tablas de BD)
│   │   ├── usuario.py
│   │   ├── liga.py
│   │   └── ...
│   │
│   ├── schemas/              # Los formularios (validación)
│   │   ├── usuario.py
│   │   ├── liga.py
│   │   └── ...
│   │
│   └── database/
│       └── connection.py     # El cable que conecta con MySQL
│
├── .env                      # Los secretos
├── requirements.txt          # La lista de compras
└── README.md                 # Las instrucciones
```

### ¿Qué hace cada archivo?

| Archivo/Carpeta | Analogía | ¿Qué hace? |
|-----------------|----------|------------|
| `main.py` | El gerente del restaurante | Inicia todo y coordina |
| `config.py` | El libro de reglas | Lee las configuraciones |
| `routers/` | Los meseros | Reciben los pedidos del cliente |
| `services/` | La cocina | Preparan las respuestas |
| `models/` | La organización de la despensa | Definen cómo se guardan los datos |
| `schemas/` | Los formularios de pedido | Verifican que los datos estén correctos |
| `database/` | El cable a la nevera | Conecta con MySQL |

### ¿Por qué esta estructura?

**Alternativa desordenada (❌):**

```
backend/
├── cosas.py           # ¿Qué hay aquí?
├── mas_cosas.py       # ¿Y aquí?
├── usuarios.py        # ¿Router? ¿Service? ¿Model? ¿Quién sabe?
├── auth.py            # ¿Todo mezclado?
└── main.py            # ¡Socorro!
```

**Nuestra estructura organizada (✅):**

```
backend/
├── api/
│   ├── routers/       # Aquí están los endpoints
│   └── services/      # Aquí está la lógica
├── models/            # Aquí están las tablas
├── schemas/           # Aquí están las validaciones
```

**Ventajas:**

1. **Fácil de encontrar:** "¿Dónde está el endpoint de usuarios?" → `routers/usuarios.py`
2. **Fácil de mantener:** Cambias una cosa y no rompes otra
3. **Fácil de trabajar en equipo:** Cada persona trabaja en una carpeta

---

## Los Componentes Principales

### 1. `main.py` - El Jefe

```python
from fastapi import FastAPI
from .config import settings
from .database.connection import engine, Base
from .api.routers import auth, usuarios, ligas

# Lo que pasa al iniciar la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear las tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    yield  # La app corre aquí
    # Al apagar, cerrar conexiones
    engine.dispose()

# Crear la aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Registrar los routers (contratar a los meseros)
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(ligas.router, prefix="/api/v1", tags=["Ligas"])
```

**¿Qué hace cada parte?**

| Línea | ¿Qué hace? |
|-------|------------|
| `Base.metadata.create_all()` | Crea las tablas si no existen |
| `FastAPI(...)` | Crea la aplicación |
| `include_router()` | Registra los endpoints |

### 2. `config.py` - El Libro de Reglas

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Todo lo que necesita la app
    DATABASE_URL: str           # ¿Dónde está la base de datos?
    SECRET_KEY: str             # La llave secreta
    APP_NAME: str = "Mi App"    # El nombre de la app

    # Leer del archivo .env automáticamente
    model_config = {
        "env_file": ".env",
    }

# Crear una instancia para usar en todo el proyecto
settings = Settings()
```

**¿Por qué usar una clase?**

```python
# ❌ Sin clase (confuso)
import os
DATABASE_URL = os.environ.get("DATABASE_URL")  # Puede ser None
PORT = int(os.environ.get("PORT", "8000"))     # Tienes que convertir

# ✅ Con clase (organizado)
from app.config import settings
settings.DATABASE_URL  # Ya es string, garantizado
settings.PORT           # Ya es int, convertido
```

### 3. `models/` - La Despensa

```python
# app/models/usuario.py
from sqlalchemy import Column, Integer, String, DateTime
from ..database.connection import Base

class Usuario(Base):
    # El nombre de la tabla en MySQL
    __tablename__ = "usuarios"

    # Las columnas (los campos de la tabla)
    id_usuario = Column(Integer, primary_key=True)      # El ID único
    nombre = Column(String(100), nullable=False)        # El nombre (obligatorio)
    email = Column(String(100), unique=True)            # El email (único)
    contraseña_hash = Column(String(255))               # La contraseña escondida

    # Relaciones (más adelante veremos esto)
    roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")
```

**¿Qué significa cada cosa?**

| Código | Significado |
|--------|-------------|
| `__tablename__` | El nombre de la tabla en MySQL |
| `primary_key=True` | Es el identificador único |
| `nullable=False` | Es obligatorio, no puede estar vacío |
| `unique=True` | No puede repetirse (cada email es único) |

### 4. `schemas/` - Los Formularios

```python
# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, Field

# Para crear un usuario (qué datos necesita)
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

# Para responder (qué datos devolvemos)
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Puede leer de SQLAlchemy
```

**¿Por qué schemas separados?**

| Schema | Uso | Campos |
|--------|-----|--------|
| `UsuarioCreate` | Crear usuario | `nombre`, `email`, `password` |
| `UsuarioResponse` | Responder | `id`, `nombre`, `email`, `created_at` (¡sin password!) |

**¡Nunca devuelvas la contraseña!** Por eso usamos schemas diferentes.

### 5. `services/` - La Cocina

```python
# app/api/services/usuario_service.py
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate

def crear_usuario(db: Session, datos: UsuarioCreate):
    """
    Crea un nuevo usuario.
    Esta es la lógica de negocio.
    """

    # Regla de negocio: el email debe ser único
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    # Crear el usuario
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hash_password(datos.password)  # ¡Nunca guardar la contraseña original!
    )

    # Guardar en la base de datos
    db.add(usuario)
    db.commit()
    db.refresh(usuario)  # Obtener el ID generado

    return usuario
```

**¿Por qué no poner esto en el router?**

```python
# ❌ Lógica en el router (confuso)
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(400, "Email ya existe")
    usuario = Usuario(...)
    db.add(usuario)
    db.commit()
    return usuario

# ✅ Lógica en el service (organizado)
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(db, datos)  # Limpio
    except ValueError as e:
        raise HTTPException(400, str(e))
```

**Ventajas:**

1. **Limpio:** El router solo maneja HTTP
2. **Reutilizable:** El mismo service se puede usar desde CLI, tests, etc.
3. **Fácil de probar:** Puedes probar la lógica sin peticiones HTTP

### 6. `routers/` - Los Meseros

```python
# app/api/routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.api.services.usuario_service import crear_usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

# Crear el router (como contratar un mesero especializado)
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario.

    El router SOLO:
    1. Recibe la petición
    2. Valida los datos (automático con Pydantic)
    3. Llama al service
    4. Devuelve la respuesta
    """
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**¿Qué hace el router?**

| Paso | ¿Qué hace? |
|------|------------|
| Recibir petición | `@router.post("/")` |
| Validar datos | `datos: UsuarioCreate` (automático) |
| Inyectar dependencias | `db: Session = Depends(get_db)` |
| Llamar service | `crear_usuario(db, datos)` |
| Manejar errores | `try/except` |
| Devolver respuesta | `return usuario` |

---

## Inyección de Dependencias

### ¿Qué es esto?

Imagina que cada vez que un mesero necesita algo, tiene que ir a buscarlo:

```python
# ❌ Sin inyección de dependencias
@router.post("/usuarios/")
def crear(datos: UsuarioCreate):
    # El mesero tiene que conseguir todo solo
    db = SessionLocal()  # Crear conexión a BD
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    finally:
        db.close()  # ¡No olvidar cerrar!
```

**Problema:**
- Código repetido en cada endpoint
- Fácil olvidar cerrar la conexión
- Difícil de probar

**Con inyección de dependencias (✅):**

```python
# La dependencia
def get_db():
    db = SessionLocal()  # Crear conexión
    try:
        yield db          # Dar la conexión
    finally:
        db.close()        # Siempre se cierra

# El router
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # db ya está listo y se cerrará automáticamente
    return crear_usuario(db, datos)
```

**Ventaja:**

El router no se preocupa por crear ni cerrar la conexión. **FastAPI lo hace automáticamente.**

### Dependencias para Autenticación

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Esta dependencia:
    1. Extrae el token del header
    2. Verifica que sea válido
    3. Busca al usuario
    4. Devuelve al usuario
    """
    payload = jwt.decode(token, SECRET_KEY)
    user_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(401, "No autorizado")
    return usuario

# Uso
@router.get("/me")
def mi_perfil(current_user = Depends(get_current_user)):
    # Si llegamos aquí, el usuario ya está autenticado
    return current_user
```

---

## El Flujo Completo (Resumen)

```
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENTE (Frontend/Móvil)                                           │
│  "Quiero crear un usuario"                                          │
│  POST /api/v1/usuarios/                                             │
│  {"nombre": "Juan", "email": "juan@email.com", "password": "123"}   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ROUTER (usuarios.py)                                                │
│  1. Recibe la petición HTTP                                          │
│  2. Valida los datos con UsuarioCreate schema                        │
│     - ¿nombre tiene al menos 2 caracteres? ✅                        │
│     - ¿email es un email válido? ✅                                  │
│     - ¿password tiene al menos 6 caracteres? ✅                      │
│  3. Inyecta la base de datos (get_db)                                │
│  4. Llama al service                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SERVICE (usuario_service.py)                                        │
│  1. Verifica reglas de negocio:                                      │
│     - ¿El email ya existe? ❌ → ERROR                                │
│     - ¿El email ya existe? ✅ → Continuar                            │
│  2. Hashea la contraseña (seguridad)                                 │
│  3. Crea el objeto Usuario                                           │
│  4. Llama al model para guardar                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  MODEL (Usuario)                                                     │
│  1. Mapea el objeto a SQL                                            │
│  2. Ejecuta: INSERT INTO usuarios (nombre, email, ...) VALUES (...)  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BASE DE DATOS (MySQL)                                               │
│  1. Guarda el usuario                                                │
│  2. Genera el ID automáticamente                                     │
│  3. Devuelve el usuario guardado                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SERVICE (usuario_service.py)                                        │
│  1. Recibe el usuario con ID                                         │
│  2. Devuelve al router                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ROUTER (usuarios.py)                                                │
│  1. Recibe el usuario                                                │
│  2. Convierte a UsuarioResponse                                      │
│     - ¡No incluye la contraseña!                                     │
│  3. Devuelve status 201 (Created)                                     │
│  {"id_usuario": 1, "nombre": "Juan", "email": "juan@email.com"}     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENTE (Frontend/Móvil)                                            │
│  Recibe la respuesta                                                  │
│  Muestra: "¡Usuario creado exitosamente!"                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Resumen

Aprendiste:

1. **Arquitectura en capas** = Organización como un restaurante
2. **Router** = El mesero (recibe pedidos)
3. **Service** = La cocina (prepara respuestas)
4. **Model** = La despensa (organiza datos)
5. **Schema** = Los formularios (valida datos)
6. **Database** = La nevera (guarda todo)

**¿Listo para el siguiente paso?**

Ve a **03-base-datos.md** para aprender cómo funcionan las tablas y relaciones.