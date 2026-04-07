# Base de Datos (Para Principiantes)

## ¿Qué es una Base de Datos?

Imagina que tienes una **nevera gigante** donde guardas cosas. Pero no tiras todo al azar. Tienes **cajas organizadas**:

```
┌─────────────────────────────────────────────────────┐
│                     NEVERA                           │
├─────────────────────────────────────────────────────┤
│  📦 Caja de Usuarios                                 │
│     ├── Usuario 1: Juan, juan@email.com             │
│     ├── Usuario 2: María, maria@email.com           │
│     └── Usuario 3: Pedro, pedro@email.com           │
│                                                      │
│  📦 Caja de Equipos                                  │
│     ├── Equipo 1: Real Madrid                        │
│     └── Equipo 2: Barcelona                          │
│                                                      │
│  📦 Caja de Partidos                                 │
│     └── Partido 1: Real Madrid vs Barcelona         │
└─────────────────────────────────────────────────────┘
```

**Una base de datos es igual:** organizas la información en **tablas** (cajas) con **filas** (elementos) y **columnas** (características).

---

## SQL vs ORM

### ¿Qué es SQL?

**SQL** es el idioma que habla la base de datos:

```sql
-- Crear un usuario
INSERT INTO usuarios (nombre, email) VALUES ('Juan', 'juan@email.com');

-- Buscar un usuario
SELECT * FROM usuarios WHERE id_usuario = 1;

-- Actualizar un usuario
UPDATE usuarios SET nombre = 'Juan Carlos' WHERE id_usuario = 1;

-- Borrar un usuario
DELETE FROM usuarios WHERE id_usuario = 1;
```

### El Problema de SQL

Escribir SQL directamente tiene problemas:

```python
# ❌ SQL directo (peligroso)
cursor.execute(f"SELECT * FROM usuarios WHERE id = {user_id}")
# Si user_id = "1 OR 1=1", ¡muestra TODOS los usuarios!
# Esto se llama "Inyección SQL"
```

### ¿Qué es un ORM?

**ORM** (Object-Relational Mapping) es un **traductor** entre Python y SQL:

```
Python                    ORM                    SQL
────────────────────────────────────────────────────────────
Usuario(nombre="Juan")  →  Traduce  →  INSERT INTO usuarios...
db.query(Usuario)       →  Traduce  →  SELECT * FROM usuarios
usuario.nombre = "X"    →  Traduce  →  UPDATE usuarios SET...
```

**Ventajas:**

| Sin ORM (SQL directo) | Con ORM (SQLAlchemy) |
|----------------------|---------------------|
| Escribes SQL manual | Escribes Python |
| Propenso a errores | Validación automática |
| Difícil de cambiar de BD | Cambias de BD en 1 línea |
| Inyección SQL posible | ¡Protección automática! |

---

## SQLAlchemy: El Traductor

### Conexión a la Base de Datos

```python
# app/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# El motor es el "cable" que conecta Python con MySQL
engine = create_engine(
    "mysql+pymysql://usuario:contraseña@localhost:3306/mi_base",
    echo=True,           # Muestra las consultas SQL en pantalla
    pool_pre_ping=True,  # Verifica que la conexión esté viva
    pool_recycle=3600,   # Renueva la conexión cada hora
    pool_size=10,        # Mantiene 10 conexiones listas
    max_overflow=20      # Puede crear 20 más si es necesario
)

# La fábrica de sesiones (donde se crean las conexiones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La base para todos los modelos (como una plantilla)
Base = declarative_base()
```

### ¿Qué significa cada parte?

| Código | ¿Qué hace? | Analogía |
|--------|------------|----------|
| `create_engine()` | Crea el cable a MySQL | El cable de la nevera |
| `echo=True` | Muestra las consultas SQL | Ver lo que cocina el chef |
| `pool_pre_ping=True` | Verifica que la conexión funcione | Tocar antes de abrir |
| `pool_size=10` | Mantiene 10 conexiones listas | 10 operadores esperando |
| `SessionLocal` | Fábrica de conexiones | La oficina del call center |
| `Base` | La plantilla para modelos | El molde de las cajas |

### SQLite vs MySQL

**SQLite** es como una nevera portátil (un archivo):

```python
# Para desarrollo y pruebas
engine = create_engine("sqlite:///mi_base.db")
```

**MySQL** es como una nevera industrial (servidor):

```python
# Para producción
engine = create_engine(
    "mysql+pymysql://usuario:contraseña@servidor:3306/mi_base",
    pool_size=10,  # MySQL necesita un pool de conexiones
)
```

---

## Modelos: Las Cajas de la Nevera

### Crear un Modelo

```python
# app/models/usuario.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database.connection import Base

class Usuario(Base):
    # El nombre de la tabla en MySQL
    __tablename__ = "usuarios"

    # Las columnas (los campos de la tabla)
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    contraseña_hash = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relaciones (las veremos más adelante)
    roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")
```

### ¿Qué significa cada cosa?

#### `__tablename__`

```python
__tablename__ = "usuarios"
```

Esto dice: "En MySQL, esta clase se llama `usuarios`".

Sin esto, SQLAlchemy usaría el nombre de la clase (`Usuario`) en minúsculas (`usuario`).

#### Columnas

```python
id_usuario = Column(Integer, primary_key=True, index=True)
#                 │         │                │
#                 │         │                └── Crea un índice (búsquedas rápidas)
#                 │         └── Es la clave primaria (identificador único)
#                 └── Es un número entero
```

```python
nombre = Column(String(100), nullable=False)
#                │             │
#                │             └── Es obligatorio (no puede estar vacío)
#                └── Es texto de máximo 100 caracteres
```

```python
email = Column(String(100), nullable=False, unique=True)
#                                    │
#                                    └── No puede repetirse (cada email es único)
```

```python
telefono = Column(String(20), nullable=True)
#                             │
#                             └── Es opcional (puede estar vacío)
```

```python
created_at = Column(DateTime, server_default=func.now())
#                         │
#                         └── MySQL pone la fecha automáticamente
```

### ¿Por qué `id_usuario` y no solo `id`?

```python
# ❌ Confuso
class Usuario(Base):
    id = Column(Integer, primary_key=True)  # ¿id de qué?

class Equipo(Base):
    id = Column(Integer, primary_key=True)  # ¿id de qué?

# En consultas:
query.filter(Usuario.id == Equipo.id)  # ¿Cuál es cuál?
```

```python
# ✅ Claro
class Usuario(Base):
    id_usuario = Column(Integer, primary_key=True)  # ID del usuario

class Equipo(Base):
    id_equipo = Column(Integer, primary_key=True)  # ID del equipo

# En consultas:
query.filter(Usuario.id_usuario == Equipo.id_usuario_entrenador)  # ¡Claro!
```

### Tipos de Datos

| Tipo SQLAlchemy | Tipo en MySQL | Para qué sirve |
|-----------------|---------------|----------------|
| `Integer` | INT | Números enteros (IDs, edades) |
| `String(n)` | VARCHAR(n) | Texto corto (nombres, emails) |
| `Text` | TEXT | Texto largo (descripciones) |
| `Boolean` | BOOLEAN | Verdadero/Falso (activo, verificado) |
| `DateTime` | DATETIME | Fechas y horas (created_at) |
| `Date` | DATE | Solo fecha (fecha_nacimiento) |
| `Float` | FLOAT | Decimales (rating: 4.5) |
| `Enum` | ENUM | Valores fijos (estado: activo, inactivo) |

```python
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, Enum

class Jugador(Base):
    __tablename__ = "jugadores"

    id_jugador = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)      # Texto hasta 100 caracteres
    bio = Column(Text)                                  # Texto largo
    activo = Column(Boolean, default=True)             # Verdadero/Falso
    fecha_nacimiento = Column(Date)                    # Solo fecha
    ultimo_login = Column(DateTime, server_default=func.now())  # Fecha y hora
    rating = Column(Float)                              # Decimal
    estado = Column(Enum("activo", "inactivo", "lesionado"))  # Valores fijos
```

### Parámetros de Columna

```python
Column(
    Integer,              # El tipo de dato
    primary_key=True,     # Es la clave primaria (identificador único)
    index=True,           # Crea un índice para búsquedas rápidas
    nullable=False,       # Es obligatorio (no puede ser NULL)
    nullable=True,        # Es opcional (puede ser NULL)
    unique=True,           # No puede repetirse
    default=True,          # Valor por defecto en Python
    server_default="now()", # Valor por defecto en MySQL
    ForeignKey("tabla.id") # Es clave foránea (relación con otra tabla)
)
```

#### ¿Diferencia entre `default` y `server_default`?

```python
# default - Python pone el valor
created_at = Column(DateTime, default=datetime.utcnow)
# Python ejecuta datetime.utcnow() antes de guardar
usuario = Usuario()  # created_at ya tiene valor aquí

# server_default - MySQL pone el valor
created_at = Column(DateTime, server_default=func.now())
# MySQL pone la fecha al hacer INSERT
usuario = Usuario()  # created_at es None
db.add(usuario)
db.commit()  # Ahora created_at tiene valor
```

---

## Relaciones entre Tablas

### Relación Uno a Muchos (1:N)

Imagina una **liga** tiene muchos **equipos**:

```
Liga: "Primera División"
├── Equipo: Real Madrid
├── Equipo: Barcelona
├── Equipo: Atlético Madrid
└── Equipo: Valencia
```

**En la base de datos:**

```sql
-- La liga es UNA
CREATE TABLE ligas (
    id_liga INT PRIMARY KEY,
    nombre VARCHAR(100)
);

-- Los equipos son MUCHOS, y cada uno tiene una liga
CREATE TABLE equipos (
    id_equipo INT PRIMARY KEY,
    nombre VARCHAR(100),
    id_liga INT,                    -- Esta es la clave foránea
    FOREIGN KEY (id_liga) REFERENCES ligas(id_liga)
);
```

**En SQLAlchemy:**

```python
class Liga(Base):
    __tablename__ = "ligas"
    id_liga = Column(Integer, primary_key=True)
    nombre = Column(String(100))

    # Una liga tiene muchos equipos
    equipos = relationship("Equipo", back_populates="liga")

class Equipo(Base):
    __tablename__ = "equipos"
    id_equipo = Column(Integer, primary_key=True)
    nombre = Column(String(100))

    # Muchos equipos pertenecen a una liga
    id_liga = Column(Integer, ForeignKey("ligas.id_liga"))
    liga = relationship("Liga", back_populates="equipos")
```

**¿Cómo se usa?**

```python
# Crear una liga con equipos
liga = Liga(nombre="Primera División")
liga.equipos = [
    Equipo(nombre="Real Madrid"),
    Equipo(nombre="Barcelona"),
]
db.add(liga)
db.commit()

# Obtener los equipos de una liga
liga = db.query(Liga).first()
for equipo in liga.equipos:  # SQLAlchemy hace el JOIN automáticamente
    print(equipo.nombre)

# Obtener la liga de un equipo
equipo = db.query(Equipo).first()
print(equipo.liga.nombre)  # ¡También funciona!
```

### ¿Qué es `relationship`?

`relationship` es la **magia** de SQLAlchemy. Te permite navegar entre tablas como si fueran objetos:

```python
# Sin relationship (❌)
equipo = db.query(Equipo).first()
liga = db.query(Liga).filter(Liga.id_liga == equipo.id_liga).first()  # Manual

# Con relationship (✅)
equipo = db.query(Equipo).first()
liga = equipo.liga  # ¡Automático!
```

### ¿Qué es `back_populates`?

`back_populates` crea una **conexión bidireccional**:

```python
# Sin back_populates (unidireccional)
class Liga(Base):
    equipos = relationship("Equipo")  # Liga → Equipo funciona

class Equipo(Base):
    pass  # Equipo → Liga NO funciona

liga.equipos  # ✅ Funciona
equipo.liga   # ❌ Error: no existe

# Con back_populates (bidireccional)
class Liga(Base):
    equipos = relationship("Equipo", back_populates="liga")

class Equipo(Base):
    liga = relationship("Liga", back_populates="equipos")

liga.equipos  # ✅ Funciona
equipo.liga   # ✅ También funciona
```

### Relación Muchos a Muchos (N:N)

Imagina que un **usuario** puede tener muchos **roles**, y un **rol** puede tener muchos **usuarios**:

```
Usuarios                  Roles
├── Juan (Admin, Editor)  ├── Admin
├── María (Editor)        ├── Editor
└── Pedro (Viewer)        └── Viewer
```

**¿Cómo se representa en la base de datos?**

Necesitas una **tabla intermedia**:

```sql
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY,
    nombre VARCHAR(100)
);

CREATE TABLE roles (
    id_rol INT PRIMARY KEY,
    nombre VARCHAR(50)
);

-- Tabla intermedia (la conexión)
CREATE TABLE usuario_rol (
    id_usuario_rol INT PRIMARY KEY,
    id_usuario INT,
    id_rol INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);
```

**En SQLAlchemy:**

```python
# Tabla intermedia (no necesita clase, solo la tabla)
usuario_rol = Table(
    'usuario_rol',
    Base.metadata,
    Column('id_usuario_rol', Integer, primary_key=True),
    Column('id_usuario', Integer, ForeignKey('usuarios.id_usuario')),
    Column('id_rol', Integer, ForeignKey('roles.id_rol'))
)

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100))

    # Un usuario tiene muchos roles (a través de la tabla intermedia)
    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")

class Rol(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(50))

    # Un rol tiene muchos usuarios
    usuarios = relationship("Usuario", secondary=usuario_rol, back_populates="roles")
```

**¿Cómo se usa?**

```python
# Crear roles
admin = Rol(nombre="admin")
editor = Rol(nombre="editor")

# Crear usuario con roles
usuario = Usuario(nombre="Juan")
usuario.roles = [admin, editor]  # Asignar múltiples roles

db.add(usuario)
db.commit()

# Obtener los roles de un usuario
usuario = db.query(Usuario).first()
for rol in usuario.roles:
    print(rol.nombre)  # "admin", "editor"

# Obtener los usuarios de un rol
rol = db.query(Rol).filter(Rol.nombre == "admin").first()
for usuario in rol.usuarios:
    print(usuario.nombre)
```

---

## El Problema N+1 y Lazy Loading

### ¿Qué es Lazy Loading?

Lazy Loading significa: "No cargues los datos hasta que los necesites".

```python
# Lazy Loading (por defecto)
usuario = db.query(Usuario).first()  # 1 query
print(usuario.roles)  # 1 query adicional (se carga ahora)
```

### El Problema N+1

```python
# Obtener 10 usuarios
usuarios = db.query(Usuario).limit(10).all()  # 1 query

# Para cada usuario, obtener sus roles
for usuario in usuarios:
    print(usuario.roles)  # 10 queries adicionales!

# Total: 1 + 10 = 11 queries
```

**¿Por qué es malo?**

Imagina que tienes 1,000 usuarios. ¡Haces 1,001 queries!

### Solución: Eager Loading

Eager Loading significa: "Carga todo de una vez".

```python
from sqlalchemy.orm import joinedload

# Eager Loading
usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()
# 1 query con JOIN

for usuario in usuarios:
    print(usuario.roles)  # Ya está cargado, 0 queries adicionales

# Total: 1 query
```

**Comparación:**

| Método | Queries | Cuándo usar |
|--------|---------|-------------|
| Lazy Loading | 1 + N | Cuando NO siempre necesitas la relación |
| Eager Loading | 1 | Cuando SIEMPRE necesitas la relación |

---

## Sesiones de Base de Datos

### ¿Qué es una Sesión?

Una **sesión** es como una **conversación temporal** con la base de datos:

```python
# Crear una sesión
db = SessionLocal()

# Hacer cosas
usuario = Usuario(nombre="Juan")
db.add(usuario)      # Agregar a la sesión (todavía no guardado)
db.commit()          # ¡Ahora sí se guarda!

# Cerrar la sesión
db.close()
```

### El Patrón por Petición

En FastAPI, cada petición HTTP tiene su propia sesión:

```python
# app/api/dependencies.py
def get_db():
    db = SessionLocal()  # Crear sesión nueva
    try:
        yield db          # Dar la sesión al endpoint
    finally:
        db.close()        # Siempre cerrar, incluso si hay error
```

```python
# En el router
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # db ya está creado y se cerrará automáticamente
    return crear_usuario(db, datos)
```

### ¿Por qué `autocommit=False`?

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Con `autocommit=True` (❌):**

```python
usuario = Usuario(nombre="Juan")
db.add(usuario)  # ¡Ya está guardado!
# No hay vuelta atrás
```

**Con `autocommit=False` (✅):**

```python
usuario = Usuario(nombre="Juan")
db.add(usuario)  # Solo en memoria, no guardado
db.commit()      # ¡Ahora sí se guarda!
# Si hay error antes de commit, nada se guarda
```

### Operaciones CRUD

#### CREATE (Crear)

```python
# Crear un usuario
usuario = Usuario(
    nombre="Juan",
    email="juan@email.com",
    contraseña_hash=hash_password("mi_contraseña")
)

# Agregar a la sesión
db.add(usuario)     # En memoria, no guardado todavía

# Guardar en la base de datos
db.commit()         # ¡Ahora sí está guardado!

# Refrescar para obtener valores generados (como el ID)
db.refresh(usuario)
print(usuario.id_usuario)  # Ahora tiene el ID
```

#### READ (Leer)

```python
# Obtener todos
usuarios = db.query(Usuario).all()

# Obtener uno por ID
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()

# Obtener uno por email
usuario = db.query(Usuario).filter(Usuario.email == "juan@email.com").first()

# Obtener varios con filtro
usuarios = db.query(Usuario).filter(Usuario.nombre.like("%Juan%")).all()

# Obtener con ordenamiento
usuarios = db.query(Usuario).order_by(Usuario.nombre).all()

# Obtener con paginación
usuarios = db.query(Usuario).offset(0).limit(10).all()  # Los primeros 10
usuarios = db.query(Usuario).offset(10).limit(10).all() # Del 11 al 20
```

#### UPDATE (Actualizar)

```python
# Obtener el usuario
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()

# Modificar
usuario.nombre = "Juan Carlos"
usuario.telefono = "+34123456789"

# Guardar
db.commit()
```

#### DELETE (Eliminar)

```python
# Obtener el usuario
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()

# Eliminar
db.delete(usuario)
db.commit()
```

### ¿Qué pasa si hay relaciones?

```python
# Si intentas eliminar un usuario que tiene roles...
usuario = db.query(Usuario).first()
db.delete(usuario)
db.commit()  # ERROR: foreign key constraint
```

**Solución 1: CASCADE (eliminar en cascada)**

```python
class Usuario(Base):
    roles = relationship("Rol", secondary="usuario_rol", cascade="delete")
```

**Solución 2: Eliminar relaciones primero**

```python
# Eliminar los roles del usuario
db.query(UsuarioRol).filter(UsuarioRol.id_usuario == usuario.id_usuario).delete()
# Eliminar el usuario
db.delete(usuario)
db.commit()
```

---

## Migraciones con Alembic

### ¿Qué es una Migración?

Imagina que tienes una tabla `usuarios`:

```
usuarios
├── id_usuario
├── nombre
└── email
```

Ahora quieres agregar un campo `telefono`. ¿Cómo lo haces sin perder los datos?

**Una migración** es como una **receta para cambiar la base de datos**:

```python
# migrations/001_add_telefono.py
def upgrade():
    op.add_column('usuarios', Column('telefono', String(20)))

def downgrade():
    op.drop_column('usuarios', 'telefono')
```

### Configurar Alembic

```bash
# Instalar
pip install alembic

# Inicializar
alembic init alembic
```

### Configurar `alembic/env.py`

```python
from app.database.connection import Base
from app.config import settings

# Configurar la URL de la base de datos
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Decirle a Alembic dónde están los modelos
target_metadata = Base.metadata
```

### Comandos Útiles

```bash
# Crear una migración automáticamente (detecta cambios en modelos)
alembic revision --autogenerate -m "Añadir campo telefono a usuarios"

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Revertir la última migración
alembic downgrade -1

# Ver el historial de migraciones
alembic history
```

### Flujo de Trabajo

```
1. Modificas un modelo (añades campo telefono)
   ↓
2. Generas migración: alembic revision --autogenerate -m "añadir telefono"
   ↓
3. Revisas el archivo generado
   ↓
4. Aplicas: alembic upgrade head
   ↓
5. La base de datos tiene el nuevo campo
```

### ⚠️ Cuidado con Autogenerate

Alembic detecta cambios automáticamente, pero **no es perfecto**:

```python
# Si comentas un modelo por error...
# class Usuario(Base):  # ¡Ups!
#     ...

# Alembic detecta que "no existe" y genera:
# def downgrade(): DROP TABLE usuarios;  # ¡PELIGROSO!
```

**Siempre revisa el archivo generado antes de aplicar.**

---

## Resumen

Aprendiste:

1. **Base de datos** = Una nevera organizada con cajas (tablas)
2. **SQL** = El idioma que habla la base de datos
3. **ORM** = Un traductor de Python a SQL
4. **Modelos** = Las cajas que organizan los datos
5. **Relaciones** = Conexiones entre cajas
   - Uno a Muchos: Una liga tiene muchos equipos
   - Muchos a Muchos: Un usuario tiene muchos roles
6. **Sesiones** = Conversaciones temporales con la base de datos
7. **Migraciones** = Recetas para cambiar la base de datos

**¿Listo para el siguiente paso?**

Ve a **04-schemas.md** para aprender cómo validar los datos que entran y salen.