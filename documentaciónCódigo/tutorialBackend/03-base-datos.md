# Base de Datos

## Conexión

### `database/connection.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..config import settings

# Configuración diferente para SQLite vs MySQL
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

> **¿Por qué configuración diferente para SQLite y MySQL?**
>
> **SQLite** está diseñado para aplicaciones embebidas de un solo proceso:
>
> - `check_same_thread=False`: SQLite por defecto solo permite acceso desde el thread que creó la conexión. FastAPI usa múltiples threads, así que necesitamos desactivar esta restricción.
> - SQLite no tiene concepto de "pool de conexiones" porque es un archivo local.
> - Útil para desarrollo y tests, **nunca para producción**.
>
> **MySQL** es un servidor cliente-servidor que requiere pool de conexiones:
>
> | Parámetro | Valor | ¿Por qué? |
> |-----------|-------|-----------|
> | `pool_pre_ping=True` | Habilitado | MySQL cierra conexiones inactivas por timeout (`wait_timeout`). Sin esto, obtienes errores intermitentes como "MySQL server has gone away" después de períodos de inactividad. |
> | `pool_recycle=3600` | 1 hora | Fuerza la reconexión cada hora. Previene problemas con firewalls que cierran conexiones TCP idle, y conexiones corruptas por timeouts del servidor. |
> | `pool_size=10` | 10 conexiones | Conexiones permanentemente abiertas. Suficiente para aplicaciones típicas. Cada conexión consume ~1MB de memoria en el servidor MySQL. |
> | `max_overflow=20` | 20 extra | Conexiones temporales cuando el pool está lleno. Total máximo = 10 + 20 = 30. Útil para picos de tráfico. |

> **¿Qué hace cada objeto?**
>
> | Objeto | Propósito | Ciclo de vida |
> |--------|----------|---------------|
> | `engine` | Motor de conexión que gestiona el pool | Global, vive toda la aplicación |
> | `SessionLocal` | Fábrica de sesiones | Global, no es una sesión en sí |
> | `Base` | Clase base para todos los modelos | Global, define metadata |
>
> **¿Por qué `autocommit=False`?**
>
> ```python
> # Con autocommit=True (PELIGROSO)
> usuario = Usuario(nombre="Juan")
> db.add(usuario)  # Ya está en la BD, no hay rollback posible
>
> # Con autocommit=False (SEGURO)
> usuario = Usuario(nombre="Juan")
> db.add(usuario)  # No está en BD todavía
> db.rollback()    # Deshacer cambios, como si nada hubiera pasado
> ```
>
> **Beneficios de autocommit=False:**
> - Transacciones atómicas: todo se guarda o nada se guarda
> - Rollback en caso de error
> - Control explícito de cuándo persistir cambios

> **¿Por qué `autoflush=False`?**
>
> ```python
> # Con autoflush=True (default)
> usuario = Usuario(nombre="Juan")
> db.add(usuario)
> db.query(Usuario).all()  # Flush automático: envía INSERT antes del SELECT
>                          # Problema: queries innecesarias
>
> # Con autoflush=False
> usuario = Usuario(nombre="Juan")
> db.add(usuario)
> db.query(Usuario).all()  # No hay flush automático
> db.commit()              # Recién aquí se envía el INSERT
> ```

## Modelos ORM

### Estructura de un Modelo

```python
# app/models/usuario.py
from sqlalchemy import Column, Integer, String, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from ..database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # Clave primaria
    id_usuario = Column(Integer, primary_key=True, index=True)

    # Campos obligatorios
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    contraseña_hash = Column(String(255), nullable=False)

    # Campos opcionales
    telefono = Column(String(20), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)

    # Campos automáticos
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")
```

**¿Por qué heredar de `Base`?**

`Base` es la clase declarativa de SQLAlchemy que:
1. Registra la clase como mapeador ORM
2. Proporciona metadata para crear las tablas
3. Habilita el sistema de relaciones

Sin heredar de `Base`, SQLAlchemy no sabe que es un modelo ORM.

**¿Qué significa cada parámetro de Column?**

| Parámetro | ¿Qué hace? | ¿Por qué usarlo? |
|-----------|------------|-----------------|
| `primary_key=True` | Marca como clave primaria | Identificador único, necesario para todo modelo |
| `index=True` | Crea índice en la columna | Acelera búsquedas por este campo. Útil para campos que se filtran frecuentemente |
| `nullable=False` | No permite NULL | El campo es obligatorio. La BD rechazará inserts sin este valor |
| `nullable=True` | Permite NULL | El campo es opcional |
| `unique=True` | Valor único en la tabla | Para emails, usernames. Garantiza que no haya duplicados |
| `server_default=func.now()` | Valor por defecto en la BD | La BD asigna el valor, no Python. Útil para timestamps |
| `onupdate=func.now()` | Actualiza automáticamente | Se ejecuta en cada UPDATE. Mantiene `updated_at` sincronizado |

**¿Por qué `id_usuario` y no solo `id`?**

```python
# ❌ Ambiguo
class Usuario(Base):
    id = Column(Integer, primary_key=True)

class Equipo(Base):
    id = Column(Integer, primary_key=True)

# En consultas:
query.filter(Usuario.id == Equipo.id)  # ¿Qué id es cuál?
```

```python
# ✅ Claro y explícito
class Usuario(Base):
    id_usuario = Column(Integer, primary_key=True)

class Equipo(Base):
    id_equipo = Column(Integer, primary_key=True)

# En consultas:
query.filter(Usuario.id_usuario == Equipo.id_usuario_entrenador)
```

**Ventajas del prefijo `id_`:**
- Nombres únicos en toda la aplicación
- Claridad en JOINs y relaciones
- Autodocumentación: `id_usuario` es el ID del usuario

**¿Por qué `contraseña_hash` y no `contraseña`?**

```python
# ❌ Confuso - ¿está hasheada o en texto plano?
contraseña = Column(String(255))

# ✅ Claro - es un hash bcrypt
contraseña_hash = Column(String(255))
```

El nombre indica que **nunca** se almacena la contraseña original, solo su hash.
Esto recuerda a los desarrolladores que deben usar funciones de hash.

### Tipos de Columnas

| Tipo SQLAlchemy | Tipo SQL   | Uso             |
| --------------- | ---------- | --------------- |
| `Integer`       | INT        | IDs, contadores |
| `String(n)`     | VARCHAR(n) | Texto corto     |
| `Text`          | VARCHAR    | Texto largo     |
| `Boolean`       | BOOLEAN    | True/False      |
| `DateTime`      | DATETIME   | Fechas y horas  |
| `Date`          | DATE       | Solo fechas     |
| `Float`         | FLOAT      | Decimales       |
| `Enum`          | ENUM       | Valores fijos   |

> **¿Cuándo usar cada tipo?**
>
> | Tipo | Usar cuando... | Ejemplo |
> |------|----------------|---------|
> | `String(n)` | Texto con longitud máxima conocida | `nombre`, `email` (n=100) |
> | `Text` | Texto largo sin límite definido | `descripcion`, `biografia` |
> | `Boolean` | Valores binarios | `activo`, `verificado` |
> | `DateTime` | Timestamps con hora | `created_at`, `last_login` |
> | `Date` | Solo fecha sin hora | `fecha_nacimiento`, `fecha_partido` |
> | `Float` | Decimales aproximados | `rating`, `temperatura` |
> | `Enum` | Conjunto finito de valores | `estado: ['pendiente', 'activo', 'cancelado']` |
>
> **¡Cuidado con Float!**
>
> ```python
> # ❌ Float tiene problemas de precisión
> precio = Column(Float)  # 0.1 + 0.2 != 0.3 en Float
>
> # ✅ Para dinero, usar DECIMAL
> from sqlalchemy import DECIMAL
> precio = Column(DECIMAL(10, 2))  # Exacto para dinero
> ```

### Parámetros de Columna

```python
Column(
    Integer,
    primary_key=True,       # Clave primaria
    index=True,              # Crea índice
    nullable=False,          # No permite NULL
    unique=True,             # Valor único
    default=True,            # Valor por defecto en Python
    server_default="now()",  # Valor por defecto en SQL
    ForeignKey("tabla.id")   # Clave foránea
)
```

> **¿Diferencia entre `default` y `server_default`?**
>
> ```python
> # default - valor asignado por Python
> created_at = Column(DateTime, default=datetime.utcnow)
> # Se asigna cuando creas el objeto en Python:
> usuario = Usuario()  # created_at ya tiene valor
>
> # server_default - valor asignado por la BD
> created_at = Column(DateTime, server_default=func.now())
> # Se asigna cuando se hace INSERT en la BD:
> usuario = Usuario()  # created_at es None
> db.add(usuario)
> db.commit()  # Ahora created_at tiene valor
> ```
>
> **¿Cuándo usar cada uno?**
>
> | Situación | Usar |
> |-----------|------|
> | Necesitas el valor antes de commit (ej: validaciones) | `default` |
> | Valor calculado por BD (ej: `now()`, `uuid()`) | `server_default` |
> | Múltiples clientes insertando (bulk insert desde SQL) | `server_default` |
> | Tests sin BD (valor disponible inmediatamente) | `default` |

## Relaciones entre Tablas

### Relación Uno a Muchos (1:N)

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
    id_liga = Column(Integer, ForeignKey("ligas.id_liga"))

    # Un equipo pertenece a una liga
    liga = relationship("Liga", back_populates="equipos")
```

> **¿Cómo funciona esta relación?**
>
> **En la base de datos:**
> ```sql
> CREATE TABLE ligas (id_liga INT PRIMARY KEY, nombre VARCHAR(100));
> CREATE TABLE equipos (
>     id_equipo INT PRIMARY KEY,
>     nombre VARCHAR(100),
>     id_liga INT REFERENCES ligas(id_liga)  -- Clave foránea
> );
> ```
>
> **En Python:**
> ```python
> # Crear liga con equipos
> liga = Liga(nombre="Primera División")
> liga.equipos = [
>     Equipo(nombre="Equipo A"),
>     Equipo(nombre="Equipo B")
> ]
> db.add(liga)
> db.commit()
>
> # Acceder a equipos desde liga
> liga = db.query(Liga).first()
> for equipo in liga.equipos:  # SQLAlchemy hace JOIN automático
>     print(equipo.nombre)
>
> # Acceder a liga desde equipo
> equipo = db.query(Equipo).first()
> print(equipo.liga.nombre)  # JOIN automático
> ```

> **¿Qué es `back_populates`?**
>
> ```python
> # Sin back_populates (unidireccional)
> class Liga(Base):
>     equipos = relationship("Equipo")  # Liga → Equipo
>
> class Equipo(Base):
>     # No hay relación inversa
>     pass
>
> # Equipo NO puede acceder a liga.equipos
> equipo.liga  # AttributeError
>
> # Con back_populates (bidireccional)
> class Liga(Base):
>     equipos = relationship("Equipo", back_populates="liga")  # Liga → Equipo
>
> class Equipo(Base):
>     liga = relationship("Liga", back_populates="equipos")  # Equipo → Liga
>
> # Ambos lados pueden acceder
> liga.equipos  # Lista de equipos
> equipo.liga   # Liga a la que pertenece
> ```

> **¿Por qué la FK está en el lado "muchos"?**
>
> ```
> Liga (1) ──────< Equipo (N)
>                 └── id_liga (FK)
> ```
>
> - Un equipo pertenece a **una** liga → FK en equipo
> - Una liga tiene **muchos** equipos → No FK en liga
>
> Si pusieras FK en Liga:
> ```python
> # ❌ Mal diseño
> class Liga(Base):
>     id_equipo_1 = Column(Integer, ForeignKey("equipos.id_equipo"))
>     id_equipo_2 = Column(Integer, ForeignKey("equipos.id_equipo"))
>     # ¿Y si hay 20 equipos? ¿Y si se añaden más?
> ```
>
> La FK siempre va en el lado **muchos** de la relación.

### Relación Muchos a Muchos (N:N)

```python
# Tabla intermedia
class UsuarioRol(Base):
    __tablename__ = "usuario_rol"
    id_usuario_rol = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_rol = Column(Integer, ForeignKey("roles.id_rol"))

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True)

    # Relación N:N
    roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")

class Rol(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True)

    usuarios = relationship("Usuario", secondary="usuario_rol", back_populates="roles")
```

> **¿Por qué se necesita una tabla intermedia?**
>
> **El problema:**
>
> Un usuario puede tener muchos roles. Un rol puede tener muchos usuarios.
>
> ```
> Usuario ── tiene ──> Rol 1, Rol 2, Rol 3
> Rol 1 ── pertenece a ──> Usuario A, Usuario B, Usuario C
> ```
>
> **No se puede representar con una sola FK:**
>
> ```sql
> -- ❌ Imposible: un campo no puede tener múltiples valores
> CREATE TABLE usuarios (
>     id INT PRIMARY KEY,
>     roles VARCHAR(???)  -- "admin,editor,viewer"? ¡Mal diseño!
> );
> ```
>
> **Solución: Tabla intermedia**
>
> ```sql
> -- ✅ Correcto: tabla de asociación
> CREATE TABLE usuario_rol (
>     id_usuario_rol INT PRIMARY KEY,
>     id_usuario INT REFERENCES usuarios(id_usuario),
>     id_rol INT REFERENCES roles(id_rol),
>     UNIQUE(id_usuario, id_rol)  -- Evita duplicados
> );
> ```
>
> Esta tabla asocia usuarios con roles de forma limpia y normalizada.

> **¿Qué hace `secondary`?**
>
> ```python
> roles = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")
> #                                  ↑
> #                          Nombre de la tabla intermedia
> ```
>
> SQLAlchemy:
> 1. Detecta que es una relación N:N
> 2. Busca la tabla `usuario_rol`
> 3. Usa las FK para hacer JOINs automáticamente
>
> ```python
> usuario = db.query(Usuario).first()
> usuario.roles  # SQLAlchemy ejecuta:
> # SELECT roles.* FROM roles
> # JOIN usuario_rol ON roles.id_rol = usuario_rol.id_rol
> # WHERE usuario_rol.id_usuario = ?
> ```

### Lazy Loading

```python
# Cargar inmediatamente
roles = relationship("Rol", secondary="usuario_rol", lazy="select")

# Cargar con JOIN (una consulta)
roles = relationship("Rol", secondary="usuario_rol", lazy="joined")

# Cargar con subconsulta
roles = relationship("Rol", secondary="usuario_rol", lazy="subquery")
```

> **¿Qué es Lazy Loading y por qué importa?**
>
> **El problema N+1:**
>
> ```python
> # lazy="select" (default) - Lazy Loading
> usuarios = db.query(Usuario).all()  # 1 query
>
> for usuario in usuarios:
>     print(usuario.roles)  # N queries adicionales!
>
> # Total: 1 + N queries
> # Si hay 100 usuarios = 101 queries
> ```
>
> **Con Eager Loading:**
>
> ```python
> # lazy="joined" - Eager Loading
> usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()
>
> for usuario in usuarios:
>     print(usuario.roles)  # Ya están cargados
>
> # Total: 1 query con JOIN
> ```
>
> **Comparación de estrategias:**
>
> | Estrategia | Queries | Cuándo usar |
> |------------|---------|-------------|
> | `lazy="select"` | 1 + N | Cuando no siempre necesitas la relación |
> | `lazy="joined"` | 1 | Cuando siempre necesitas la relación |
> | `lazy="subquery"` | 2 | Cuando necesitas la relación pero con filtrado |
>
> **Recomendación:**
>
> ```python
> # En el modelo: lazy loading por defecto
> roles = relationship("Rol", secondary="usuario_rol")
>
> # En la query: eager loading cuando necesites
> db.query(Usuario).options(joinedload(Usuario.roles)).all()
> ```
>
> Esto da flexibilidad: lazy por defecto, eager cuando lo necesites.

## Sesiones de Base de Datos

### Patrón por Petición

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

> **¿Por qué una sesión por petición?**
>
> **Problema con sesión global:**
>
> ```python
> # ❌ PELIGROSO - Sesión global
> db = SessionLocal()
>
> @router.post("/usuarios/")
> def crear(datos: UsuarioCreate):
>     usuario = Usuario(...)
>     db.add(usuario)
>     # Si hay error aquí, db tiene estado inconsistente
>     db.commit()
>     return usuario
>
> # Problemas:
> # 1. Si hay error, la sesión queda en estado corrupto
> # 2. No hay aislamiento entre requests
> # 3. Problemas de concurrencia
> ```
>
> **Solución: Sesión por petición:**
>
> ```python
> # ✅ CORRECTO - Sesión por petición
> def get_db():
>     db = SessionLocal()  # Nueva sesión para cada request
>     try:
>         yield db
>     finally:
>         db.close()  # Siempre se cierra, incluso con error
>
> @router.post("/usuarios/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     usuario = Usuario(...)
>     db.add(usuario)
>     db.commit()
>     return usuario
>     # db.close() se ejecuta automáticamente
> ```
>
> **Beneficios:**
>
> 1. **Aislamiento**: Cada request tiene su propia sesión, sin interferencia.
> 2. **Limpieza automática**: `finally` garantiza que `db.close()` siempre se ejecuta.
> 3. **Rollback automático**: Si no hay commit explícito, los cambios se descartan al cerrar.

### Operaciones CRUD

```python
# CREATE
usuario = Usuario(nombre="Juan", email="juan@email.com")
db.add(usuario)
db.commit()
db.refresh(usuario)  # Obtener ID generado

# READ
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()
usuarios = db.query(Usuario).filter(Usuario.nombre.like("%Juan%")).all()

# UPDATE
usuario.nombre = "Juan Carlos"
db.commit()

# DELETE
db.delete(usuario)
db.commit()
```

> **¿Por qué `db.refresh()` después de INSERT?**
>
> ```python
> usuario = Usuario(nombre="Juan", email="juan@email.com")
> print(usuario.id_usuario)  # None - todavía no hay ID
>
> db.add(usuario)
> db.commit()  # INSERT ejecutado
>
> print(usuario.id_usuario)  # ¿None o ID?
> # Sin refresh: depende de la BD y driver
> # Con refresh: garantizado que tiene el ID
> db.refresh(usuario)
> print(usuario.id_usuario)  # ID generado por la BD
> ```
>
> `refresh()` hace un SELECT para obtener los valores generados por la BD:
> - `id_usuario` (autoincrement)
> - `created_at` (server_default)
> - Cualquier campo calculado por triggers

> **¿Por qué no hay commit en READ?**
>
> ```python
> # READ - solo consulta
> usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()
> # No modifica datos → no necesita commit
>
> # CREATE - modifica datos
> db.add(usuario)
> db.commit()  # Necesario para persistir
>
> # UPDATE - modifica datos
> usuario.nombre = "Nuevo"
> db.commit()  # Necesario para persistir
> ```
>
> `commit()` escribe los cambios en la BD. Las consultas SELECT no modifican nada.

> **¿Qué pasa si no hago commit?**
>
> ```python
> usuario = Usuario(nombre="Juan")
> db.add(usuario)
> # Sin commit
>
> # En la misma sesión:
> db.query(Usuario).all()  # Ve a Juan (cached)
>
> # En otra sesión/conexión:
> db2 = SessionLocal()
> db2.query(Usuario).all()  # NO ve a Juan (no commit)
> ```
>
> Los cambios sin commit solo son visibles en la misma sesión.

### Consultas con JOIN

```python
from sqlalchemy.orm import joinedload

# Cargar usuario con sus roles
usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()

# Filtrar por relación
usuarios = db.query(Usuario).join(Usuario.roles).filter(Rol.nombre == "admin").all()
```

> **¿Cuándo usar `joinedload` vs `join`?**
>
> **`joinedload` - Para cargar relaciones:**
>
> ```python
> # joinedload: CARGA la relación automáticamente
> usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()
>
> for usuario in usuarios:
>     print(usuario.roles)  # Ya está cargado, no hay query adicional
>
> # SQL generado:
> # SELECT usuarios.*, roles.* FROM usuarios
> # LEFT OUTER JOIN usuario_rol ON ...
> # LEFT OUTER JOIN roles ON ...
> ```
>
> **`join` - Para filtrar:**
>
> ```python
> # join: FILTRA por relación, pero no la carga
> usuarios = db.query(Usuario).join(Usuario.roles).filter(Rol.nombre == "admin").all()
>
> for usuario in usuarios:
>     print(usuario.roles)  # Query adicional por cada usuario (N+1)!
>
> # SQL generado:
> # SELECT usuarios.* FROM usuarios
> # JOIN usuario_rol ON ...
> # JOIN roles ON ...
> # WHERE roles.nombre = 'admin'
> ```
>
> **Combinando ambos:**
>
> ```python
> # Filtrar Y cargar
> usuarios = db.query(Usuario)\
>     .join(Usuario.roles)\
>     .filter(Rol.nombre == "admin")\
>     .options(joinedload(Usuario.roles))\
>     .all()
> ```

### Agregaciones

```python
from sqlalchemy import func

# Contar
total = db.query(func.count(Usuario.id_usuario)).scalar()

# Promedio
promedio = db.query(func.avg(Jugador.dorsal)).scalar()

# Máximo
max_dorsal = db.query(func.max(Jugador.dorsal)).scalar()
```

> **¿Por qué `scalar()` y no `all()` o `first()`?**
>
> ```python
> # Agregación devuelve un solo valor
> result = db.query(func.count(Usuario.id_usuario))
> # SQL: SELECT COUNT(usuarios.id_usuario) FROM usuarios
>
> # all() devuelve lista
> result.all()  # [5] - lista de un elemento
>
> # first() devuelve tupla
> result.first()  # (5,) - tupla
>
> # scalar() devuelve el valor directamente
> result.scalar()  # 5 - el número
> ```
>
> **Regla:**
> - `scalar()` para agregaciones que devuelven un valor
> - `first()` para obtener un registro
> - `all()` para obtener múltiples registros

## Esquema de Base de Datos

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  usuarios   │       │ usuario_rol │       │   roles     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id_usuario  │───┐   │ id_usuario  │   ┌───│ id_rol      │
│ nombre      │   └───│ id_rol      │───┘   │ nombre      │
│ email       │       │ (FK)        │       │ descripcion │
└─────────────┘       └─────────────┘       └─────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  jugadores  │       │  equipos    │───────│   ligas     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id_jugador  │       │ id_equipo   │       │ id_liga     │
│ id_usuario  │       │ nombre      │       │ nombre      │
│ id_equipo   │       │ id_liga     │       └─────────────┘
└─────────────┘       └─────────────┘
```

> **¿Por qué este diseño específico?**
>
> **Entidades principales:**
>
> | Entidad | Propósito | Relaciones |
> |---------|-----------|------------|
> | `usuarios` | Personas del sistema | N:N con roles, 1:N con jugadores |
> | `roles` | Permisos | N:N con usuarios |
> | `ligas` | Competiciones | 1:N con equipos |
> | `equipos` | Equipos de fútbol | N:1 con ligas, 1:N con jugadores |
> | `jugadores` | Jugadores de equipos | N:1 con usuarios y equipos |
>
> **¿Por qué separar `usuarios` y `jugadores`?**
>
> ```python
> # ❌ Todo en usuarios
> class Usuario(Base):
>     nombre = Column(String)
>     dorsal = Column(Integer)  # ¿Y si no es jugador?
>     posicion = Column(String)  # ¿Y si es árbitro?
>
> # ✅ Separado
> class Usuario(Base):
>     # Datos comunes a todos
>     nombre = Column(String)
>     email = Column(String)
>
> class Jugador(Base):
>     # Datos específicos de jugador
>     id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
>     dorsal = Column(Integer)
>     posicion = Column(String)
> ```
>
> **Ventajas:**
> - Un usuario puede no ser jugador (árbitro, administrador)
> - Un usuario puede ser jugador en múltiples equipos
> - Datos específicos bien organizados

## Migraciones con Alembic

### Configuración

```bash
alembic init alembic
```

### `alembic/env.py`

```python
from app.database.connection import Base
from app.config import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

> **¿Por qué usar Alembic?**
>
> **Sin migraciones:**
>
> ```python
> # Desarrollo inicial
> class Usuario(Base):
>     nombre = Column(String(50))
>
> # Necesitas añadir email...
> # ¿Cómo lo haces en producción sin perder datos?
> # ¿Cómo sincronizas con tu equipo?
> ```
>
> **Con migraciones:**
>
> ```bash
> # 1. Modificas el modelo
> class Usuario(Base):
>     nombre = Column(String(50))
>     email = Column(String(100))  # Nuevo campo
>
> # 2. Generas migración
> alembic revision --autogenerate -m "añadir email"
> # Genera: versions/abc123_añadir_email.py
>
> # 3. Aplicas en desarrollo
> alembic upgrade head
>
> # 4. En producción
> alembic upgrade head  # Misma migración
> ```
>
> **Ventajas:**
>
> 1. **Versionado**: Cada cambio en la BD está registrado y tiene un ID.
> 2. **Reproducible**: Cualquiera puede ejecutar las mismas migraciones.
> 3. **Rollback**: Puedes deshacer cambios con `downgrade`.
> 4. **Colaboración**: Los cambios viajan con el código en Git.

### Comandos

```bash
# Crear migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir
alembic downgrade -1

# Ver historial
alembic history
```

> **¿Qué hace cada comando?**
>
> | Comando | ¿Qué hace? |
> |---------|------------|
> | `revision --autogenerate -m "msg"` | Compara modelos con BD actual y genera script de migración |
> | `upgrade head` | Aplica todas las migraciones pendientes |
> | `downgrade -1` | Revierte la última migración |
> | `history` | Muestra todas las migraciones |
>
> **Flujo típico:**
>
> ```bash
> # 1. Modificas un modelo
> # Añades campo telefono a Usuario
>
> # 2. Generas migración
> alembic revision --autogenerate -m "añadir telefono a usuarios"
>
> # 3. Revisas el archivo generado
> # alembic/versions/xyz123_añadir_telefono.py
>
> # 4. Aplicas
> alembic upgrade head
>
> # Si hay error, reviertes
> alembic downgrade -1
> ```

> **¿Por qué `--autogenerate` puede ser peligroso?**
>
> Alembic detecta cambios automáticamente, pero **no es perfecto**:
>
> ```python
> # Si borras un modelo por accidente...
> # class Usuario(Base):  # Comentado por error
> #     ...

# Alembic detecta que "no existe" y genera:
# downgrade(): DROP TABLE usuarios;  # ¡PELIGROSO!
> ```
>
> **Recomendación:**
>
> 1. Siempre revisa el archivo generado antes de aplicar
> 2. Nunca ejecutes `upgrade head` sin revisar en producción
> 3. Haz backup antes de migraciones importantes
> 4. Prueba las migraciones en desarrollo primero