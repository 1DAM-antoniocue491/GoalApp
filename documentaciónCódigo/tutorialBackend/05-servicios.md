# Servicios (Lógica de Negocio)

## Arquitectura

```
┌─────────────────┐
│     Router      │  ← Recibe petición HTTP, valida datos
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Servicio     │  ← Lógica de negocio
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Modelo      │  ← ORM
└─────────────────┘
```

> **¿Por qué separar la lógica en servicios?**
>
> **Sin servicios (lógica en router):**
>
> ```python
> @router.post("/usuarios/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     # ❌ Lógica de negocio mezclada con HTTP
>     existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
>     if existente:
>         raise HTTPException(400, "Email ya registrado")
>
>     hashed = bcrypt.hash(datos.password)
>     usuario = Usuario(
>         nombre=datos.nombre,
>         email=datos.email,
>         contraseña_hash=hashed
>     )
>     db.add(usuario)
>     db.commit()
>     return usuario
> ```
>
> **Problemas:**
> 1. Lógica de negocio acoplada a HTTP
> 2. Difícil de testear (necesitas simular petición HTTP)
> 3. No reutilizable (¿qué si quieres crear usuarios desde CLI?)
> 4. Router se vuelve largo y complejo
>
> **Con servicios (separación de responsabilidades):**
>
> ```python
> # router
> @router.post("/usuarios/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     try:
>         return crear_usuario(db, datos)
>     except ValueError as e:
>         raise HTTPException(400, str(e))
>
> # service
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     if db.query(Usuario).filter(Usuario.email == datos.email).first():
>         raise ValueError("Email ya registrado")
>     # ...
> ```
>
> **Ventajas:**
> | Ventaja | Descripción |
> |---------|-------------|
> | **Testeabilidad** | Tests unitarios sin HTTP |
> | **Reutilización** | Mismo servicio desde REST API, CLI, scripts |
> | **Mantenibilidad** | Lógica centralizada |
> | **Legibilidad** | Router solo maneja HTTP, service solo lógica |

## Estructura de un Servicio

```python
# app/api/services/usuario_service.py
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Genera hash bcrypt de una contraseña."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(password, hashed)
```

> **¿Por qué funciones auxiliares para contraseñas?**
>
> **Hash directo en cada función:**
>
> ```python
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     hashed = pwd_context.hash(datos.password)  # Repetido
>     # ...
>
> def cambiar_password(db: Session, user_id: int, new_password: str):
>     hashed = pwd_context.hash(new_password)  # Repetido
>     # ...
> ```
>
> **Con funciones auxiliares:**
>
> ```python
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     hashed = hash_password(datos.password)  # Función centralizada
>     # ...
>
> def cambiar_password(db: Session, user_id: int, new_password: str):
>     hashed = hash_password(new_password)  # Mismo lugar
>     # ...
> ```
>
> **Ventajas:**
> 1. **DRY (Don't Repeat Yourself)**: Lógica en un solo lugar
> 2. **Cambio fácil**: Si cambias de bcrypt a argon2, solo modifies una función
> 3. **Testing**: Puedes mockear `hash_password` en tests

> **¿Por qué `CryptContext` en lugar de `bcrypt` directo?**
>
> ```python
> # ❌ Con bcrypt directo
> import bcrypt
> hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
>
> # ✅ Con passlib CryptContext
> from passlib.context import CryptContext
> pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
> hashed = pwd_context.hash(password)
> ```
>
> **Ventajas de CryptContext:**
>
> 1. **Migración de algoritmos**: Puedes cambiar de bcrypt a argon2 gradualmente
>
>    ```python
>    pwd_context = CryptContext(
>        schemes=["argon2", "bcrypt"],  # Nuevos con argon2
>        deprecated=["bcrypt"]          #bcrypt deprecated pero sigue verificando
>    )
>    ```
>
> 2. **Verificación automática**: Detecta el algoritmo del hash automáticamente
>
>    ```python
>    # Funciona con hashes antiguos y nuevos
>    pwd_context.verify(password, old_bcrypt_hash)  # OK
>    pwd_context.verify(password, new_argon2_hash)   # OK
>    ```
>
> 3. **Configuración centralizada**: Parámetros en un lugar
>
>    ```python
>    pwd_context = CryptContext(
>        schemes=["bcrypt"],
>        bcrypt__rounds=12  # Factor de costo
>    )
>    ```

## Operaciones CRUD

### Crear

```python
def crear_usuario(db: Session, datos: UsuarioCreate):
    """
    Crea un nuevo usuario en la base de datos.

    Args:
        db: Sesión de base de datos
        datos: Datos validados del usuario

    Returns:
        Usuario: Usuario creado con ID asignado

    Raises:
        ValueError: Si el email ya está registrado
    """
    # Verificar email único
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    # Crear usuario
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

> **¿Por qué verificar email único antes del INSERT?**
>
> **Sin verificación:**
>
> ```python
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     usuario = Usuario(email=datos.email, ...)
>     db.add(usuario)
>     db.commit()  # IntegrityError si email duplicado
>     # Error genérico de base de datos
> ```
>
> **Con verificación:**
>
> ```python
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     if db.query(Usuario).filter(Usuario.email == datos.email).first():
>         raise ValueError("El email ya está registrado")  # Error claro
>     # ...
> ```
>
> **Ventajas de verificar primero:**
>
> 1. **Mensaje de error claro**: "Email ya registrado" vs "IntegrityError: duplicate key value violates unique constraint"
> 2. **Control del flujo**: Puedes manejar el error antes de tocar la BD
> 3. **HTTP status correcto**: 400 Bad Request vs 500 Internal Server Error

> **¿Por qué `db.add()` → `db.commit()` → `db.refresh()`?**
>
> ```python
> usuario = Usuario(nombre="Juan", email="juan@email.com")
>
> db.add(usuario)      # 1. Añade a la sesión (pendiente)
> print(usuario.id_usuario)  # None - todavía no tiene ID
>
> db.commit()         # 2. Ejecuta INSERT en la BD
> print(usuario.id_usuario)  # Puede tener ID (depende del driver)
>
> db.refresh(usuario) # 3. Recarga desde la BD
> print(usuario.id_usuario)  # Definitivamente tiene ID
> print(usuario.created_at)  # También campos con server_default
> ```
>
> **¿Qué pasa si olvidas `commit()`?**
>
> ```python
> db.add(usuario)
> # db.commit()  # ¡Olvidado!
> db.refresh(usuario)  # Error: no existe en BD
> ```
>
> **¿Qué pasa si olvidas `refresh()`?**
>
> ```python
> db.add(usuario)
> db.commit()
> # db.refresh(usuario)  # ¡Olvidado!
> print(usuario.id_usuario)  # Puede funcionar o no, depende del driver
> print(usuario.created_at)  # None - no se recargó
> ```

### Leer

```python
def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene todos los usuarios con paginación."""
    return db.query(Usuario).offset(skip).limit(limit).all()

def obtener_usuario_por_id(db: Session, usuario_id: int):
    """Busca un usuario por su ID."""
    return db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

def obtener_usuario_por_email(db: Session, email: str):
    """Busca un usuario por su email."""
    return db.query(Usuario).filter(Usuario.email == email).first()
```

> **¿Por qué funciones separadas para cada consulta?**
>
> **Una función con parámetros:**
>
> ```python
> def buscar_usuario(db: Session, id: int = None, email: str = None):
>     query = db.query(Usuario)
>     if id:
>         query = query.filter(Usuario.id_usuario == id)
>     if email:
>         query = query.filter(Usuario.email == email)
>     return query.first()
>
> # Uso
> usuario = buscar_usuario(db, id=1)
> usuario = buscar_usuario(db, email="juan@email.com")
> ```
>
> **Problema:**
> - Firma confusa: ¿qué parámetros son obligatorios?
> - Difícil de entender qué hace cada llamada
> - No claro qué devuelve
>
> **Funciones separadas:**
>
> ```python
> # Uso claro
> usuario = obtener_usuario_por_id(db, 1)
> usuario = obtener_usuario_por_email(db, "juan@email.com")
> ```
>
> **Ventajas:**
> - Nombre descriptivo indica qué hace
> - Parámetros claros
> - Fácil de encontrar con autocompletado

> **¿Por qué `first()` y no `one()` o `all()`?**
>
> | Método | Cuándo usar | Comportamiento si no hay resultados |
> |--------|-------------|-------------------------------------|
> | `first()` | Esperas 0 o 1 resultado | Devuelve `None` |
> | `one()` | Esperas exactamente 1 resultado | Lanza excepción |
> | `all()` | Esperas múltiples resultados | Devuelve lista vacía `[]` |
> | `one_or_none()` | Esperas 0 o 1 resultado | Devuelve `None`, error si > 1 |
>
> ```python
> # Para búsqueda por ID (0 o 1 resultado)
> usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()
> if usuario is None:
>     raise HTTPException(404, "Usuario no encontrado")
>
> # Para email único (0 o 1 resultado)
> usuario = db.query(Usuario).filter(Usuario.email == email).first()
>
> # Para listar (múltiples resultados)
> usuarios = db.query(Usuario).all()
>
> # Para casos donde esperas exactamente 1
> try:
>     usuario = db.query(Usuario).filter(Usuario.email == email).one()
> except NoResultFound:
>     # Manejar error
> ```
>
> **Recomendación:**
> - `first()` para búsquedas por campo único (id, email)
> - `all()` para listas
> - `one()` solo cuando estás 100% seguro que debe existir exactamente uno

### Actualizar

```python
def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate):
    """Actualiza un usuario existente."""
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    if datos.nombre is not None:
        usuario.nombre = datos.nombre

    if datos.email is not None:
        existente = db.query(Usuario).filter(
            Usuario.email == datos.email,
            Usuario.id_usuario != usuario_id
        ).first()
        if existente:
            raise ValueError("El email ya está en uso")
        usuario.email = datos.email

    if datos.contraseña is not None:
        usuario.contraseña_hash = hash_password(datos.contraseña)

    db.commit()
    db.refresh(usuario)
    return usuario
```

> **¿Por qué verificar `is not None` en cada campo?**
>
> **Sin verificación:**
>
> ```python
> def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate):
>     usuario = db.query(Usuario).filter(...).first()
>     usuario.nombre = datos.nombre      # Si es None, ¡borra el nombre!
>     usuario.email = datos.email        # Si es None, ¡borra el email!
>     db.commit()
> ```
>
> **Con verificación:**
>
> ```python
> def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate):
>     usuario = db.query(Usuario).filter(...).first()
>
>     # Solo actualizar si se proporcionó el campo
>     if datos.nombre is not None:
>         usuario.nombre = datos.nombre
>
>     if datos.email is not None:
>         usuario.email = datos.email
>
>     db.commit()
> ```
>
> **¿Por qué no usar `datos.dict()`?**
>
> ```python
> # ❌ Peligroso - actualiza todos los campos
> for key, value in datos.dict().items():
>     setattr(usuario, key, value)  # None sobrescribe valores existentes
>
> # ✅ Correcto - excluir None
> for key, value in datos.dict(exclude_unset=True).items():
>     setattr(usuario, key, value)
> ```
>
> **`exclude_unset=True`** solo incluye campos que el cliente envió explícitamente.

> **¿Por qué verificar email duplicado al actualizar?**
>
> **Escenario problemático:**
>
> 1. Usuario A tiene email `juan@email.com`
> 2. Usuario B intenta actualizar su email a `juan@email.com`
>
> **Sin verificación:**
>
> ```python
> # Error: IntegrityError (duplicate key)
> usuario.email = datos.email
> db.commit()  # ¡CRASH!
> ```
>
> **Con verificación:**
>
> ```python
> # Excluir el usuario actual de la búsqueda
> existente = db.query(Usuario).filter(
>     Usuario.email == datos.email,
>     Usuario.id_usuario != usuario_id  # ¡No buscar a sí mismo!
> ).first()
>
> if existente:
>     raise ValueError("El email ya está en uso")
> ```
>
> **¿Por qué `Usuario.id_usuario != usuario_id`?**
>
> Si el usuario actualiza su propio perfil sin cambiar el email:
>
> ```python
> # Sin excluirse a sí mismo
> usuario = obtener_usuario_por_id(db, 1)  # email: juan@email.com
> datos = UsuarioUpdate(email="juan@email.com")  # Mismo email
>
> # Verificación falla porque encuentra su propio email
> existente = db.query(Usuario).filter(Usuario.email == "juan@email.com").first()
> # existente es el mismo usuario!
>
> # Con exclusión
> existente = db.query(Usuario).filter(
>     Usuario.email == "juan@email.com",
>     Usuario.id_usuario != 1  # Excluirse a sí mismo
> ).first()
> # existente es None, OK continuar
> ```

### Eliminar

```python
def eliminar_usuario(db: Session, usuario_id: int):
    """Elimina un usuario."""
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    db.delete(usuario)
    db.commit()
```

> **¿Por qué `db.delete()` + `db.commit()`?**
>
> ```python
> db.delete(usuario)  # Marca para eliminación (en sesión)
> # No se elimina todavía de la BD
>
> db.commit()  # Ejecuta DELETE FROM usuarios WHERE id = ?
> ```
>
> **¿Qué pasa si hay relaciones?**
>
> ```python
> # Usuario tiene relaciones con roles
> usuario = db.query(Usuario).first()
> db.delete(usuario)
> db.commit()  # IntegrityError: foreign key constraint
> ```
>
> **Soluciones:**
>
> 1. **CASCADE en modelo:**
>
>    ```python
>    class Usuario(Base):
>        roles = relationship("Rol", secondary="usuario_rol", cascade="delete")
>    ```
>
> 2. **Eliminar relaciones primero:**
>
>    ```python
>    # Eliminar roles del usuario
>    db.query(UsuarioRol).filter(UsuarioRol.id_usuario == usuario_id).delete()
>    # Eliminar usuario
>    db.delete(usuario)
>    db.commit()
>    ```
>
> 3. **Soft delete (eliminación lógica):**
>
>    ```python
>    class Usuario(Base):
>        activo = Column(Boolean, default=True)
>
>    def eliminar_usuario(db: Session, usuario_id: int):
>        usuario = obtener_usuario_por_id(db, usuario_id)
>        usuario.activo = False  # No eliminar, solo marcar
>        db.commit()
>    ```

## Consultas con SQLAlchemy

### Consultas básicas

```python
# Todos los registros
usuarios = db.query(Usuario).all()

# Por ID
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()

# Con condiciones
usuarios = db.query(Usuario).filter(
    Usuario.nombre.like("%Juan%"),
    Usuario.email.endswith("@gmail.com")
).all()

# Ordenar
usuarios = db.query(Usuario).order_by(Usuario.nombre).all()

# Paginación
usuarios = db.query(Usuario).offset(0).limit(10).all()
```

> **Desglose de cada consulta:**
>
> **`db.query(Usuario).all()`**
>
> ```sql
> SELECT * FROM usuarios;
> ```
> - Devuelve lista (puede ser vacía)
> - Carga todos los campos
> - ¡Cuidado con tablas grandes!
>
> **`db.query(Usuario).filter(Usuario.id_usuario == 1).first()`**
>
> ```sql
> SELECT * FROM usuarios WHERE id_usuario = 1 LIMIT 1;
> ```
> - `first()` añade LIMIT 1 implícitamente
> - Devuelve None si no encuentra
>
> **`db.query(Usuario).filter(Usuario.nombre.like("%Juan%"))`**
>
> ```sql
> SELECT * FROM usuarios WHERE nombre LIKE '%Juan%';
> ```
> - `%` es wildcard en SQL (cualquier texto)
> - `like` es case-insensitive en MySQL, case-sensitive en PostgreSQL
>
> **`db.query(Usuario).order_by(Usuario.nombre)`**
>
> ```sql
> SELECT * FROM usuarios ORDER BY nombre;
> ```
> - Orden ascendente por defecto
> - `.order_by(desc(Usuario.nombre))` para descendente
>
> **`db.query(Usuario).offset(0).limit(10)`**
>
> ```sql
> SELECT * FROM usuarios LIMIT 10 OFFSET 0;
> ```
> - `offset`: cuántos registros saltar
> - `limit`: cuántos registros devolver
> - Para página 2: `offset(10).limit(10)`

> **¿Por qué encadenar métodos (method chaining)?**
>
> SQLAlchemy usa el patrón **Builder**:
>
> ```python
> # Cada método devuelve un nuevo objeto query
> query = db.query(Usuario)          # Query base
> query = query.filter(...)          # Añade WHERE
> query = query.order_by(...)        # Añade ORDER BY
> query = query.limit(...)           # Añade LIMIT
> resultados = query.all()           # Ejecuta
> ```
>
> **Ventajas:**
> - Legible: se lee de izquierda a derecha
> - Flexible: puedes añadir condiciones condicionalmente
>
> ```python
> query = db.query(Usuario)
>
> if nombre:
>     query = query.filter(Usuario.nombre.ilike(f"%{nombre}%"))
>
> if email:
>     query = query.filter(Usuario.email == email)
>
> if activo:
>     query = query.filter(Usuario.activo == True)
>
> usuarios = query.all()
> ```

### JOIN

```python
from sqlalchemy.orm import joinedload

# Cargar relación
usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()

# Filtrar por relación
usuarios = db.query(Usuario).join(Usuario.roles).filter(
    Rol.nombre == "admin"
).all()
```

> **¿Por qué `joinedload` para relaciones?**
>
> **El problema N+1:**
>
> ```python
> # Sin joinedload
> usuarios = db.query(Usuario).all()  # 1 query
>
> for usuario in usuarios:
>     print(usuario.roles)  # N queries adicionales!
>
> # Si hay 100 usuarios = 101 queries
> ```
>
> **SQL ejecutado:**
>
> ```sql
> -- Query 1: Obtener usuarios
> SELECT * FROM usuarios;
>
> -- Query 2-101: Para cada usuario
> SELECT roles.* FROM roles
> JOIN usuario_rol ON roles.id_rol = usuario_rol.id_rol
> WHERE usuario_rol.id_usuario = 1;
>
> SELECT roles.* FROM roles
> JOIN usuario_rol ON roles.id_rol = usuario_rol.id_rol
> WHERE usuario_rol.id_usuario = 2;
>
> -- ... y así 100 veces
> ```
>
> **Con `joinedload`:**
>
> ```python
> usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()
>
> for usuario in usuarios:
>     print(usuario.roles)  # Ya están cargados
>
> # Solo 1 query con JOIN
> ```
>
> **SQL ejecutado:**
>
> ```sql
> SELECT usuarios.*, roles.*
> FROM usuarios
> LEFT OUTER JOIN usuario_rol ON usuarios.id_usuario = usuario_rol.id_usuario
> LEFT OUTER JOIN roles ON usuario_rol.id_rol = roles.id_rol;
> ```

> **¿Diferencia entre `join()` y `joinedload()`?**
>
> | Método | Propósito | Resultado |
> |--------|-----------|-----------|
> | `join()` | Filtrar resultados | Solo filtra, no carga la relación |
> | `joinedload()` | Cargar relación | Carga la relación automáticamente |
>
> ```python
> # join() - Solo filtra
> usuarios = db.query(Usuario).join(Usuario.roles).filter(Rol.nombre == "admin")
> # usuarios[0].roles → Query adicional (lazy loading)
>
> # joinedload() - Solo carga
> usuarios = db.query(Usuario).options(joinedload(Usuario.roles))
> # usuarios[0].roles → Ya cargado
>
> # Ambos - Filtrar Y cargar
> usuarios = db.query(Usuario)\
>     .join(Usuario.roles)\
>     .filter(Rol.nombre == "admin")\
>     .options(joinedload(Usuario.roles))
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

> **¿Qué funciones de agregación existen?**
>
> | Función | SQL | Uso |
> |---------|-----|-----|
> | `func.count()` | COUNT | Contar registros |
> | `func.sum()` | SUM | Sumar valores |
> | `func.avg()` | AVG | Promedio |
> | `func.min()` | MIN | Valor mínimo |
> | `func.max()` | MAX | Valor máximo |
>
> **Ejemplos prácticos:**
>
> ```python
> # Total de usuarios
> total_usuarios = db.query(func.count(Usuario.id_usuario)).scalar()
>
> # Usuarios activos
> usuarios_activos = db.query(func.count(Usuario.id_usuario)).filter(
>     Usuario.activo == True
> ).scalar()
>
> # Promedio de edad
> edad_promedio = db.query(func.avg(Usuario.edad)).scalar()
>
> # Suma de goles de un equipo
> total_goles = db.query(func.sum(Jugador.goles)).filter(
>     Jugador.id_equipo == equipo_id
> ).scalar()
> ```
>
> **Agregaciones con GROUP BY:**
>
> ```python
> from sqlalchemy import func
>
> # Contar usuarios por rol
> resultado = db.query(
>     Rol.nombre,
>     func.count(Usuario.id_usuario)
> ).join(Usuario.roles).group_by(Rol.nombre).all()
>
> # resultado = [("admin", 5), ("editor", 10), ("viewer", 50)]
> ```

## Transacciones

SQLAlchemy maneja transacciones automáticamente:

```python
def transferir_puntos(db: Session, de_id: int, a_id: int, puntos: int):
    try:
        usuario_origen = db.query(Usuario).filter(Usuario.id_usuario == de_id).first()
        usuario_destino = db.query(Usuario).filter(Usuario.id_usuario == a_id).first()

        usuario_origen.puntos -= puntos
        usuario_destino.puntos += puntos

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
```

> **¿Qué es una transacción?**
>
> Una transacción es un conjunto de operaciones que se ejecutan como una unidad:
> - O todas tienen éxito
> - O ninguna se aplica (rollback)
>
> **Sin transacción:**
>
> ```python
> # Transferir puntos
> usuario_origen.puntos -= puntos
> db.commit()  # ¡Si hay error aquí, los puntos se fueron!
>
> usuario_destino.puntos += puntos
> db.commit()  # ¡Ahora el destino recibe puntos que no existían!
> ```
>
> **Con transacción:**
>
> ```python
> try:
>     usuario_origen.puntos -= puntos
>     usuario_destino.puntos += puntos
>     db.commit()  # Todo junto
> except Exception:
>     db.rollback()  # Nada se aplica
>     raise
> ```

> **¿Por qué `db.rollback()` explícito?**
>
> SQLAlchemy usa **autocommit=False** por defecto, lo que significa:
> - Los cambios están en la sesión hasta que haces `commit()`
> - Si hay error, los cambios están pendientes
>
> ```python
> try:
>     usuario.nombre = "Nuevo nombre"
>     usuario.email = "email@invalido"  # Error: email duplicado
>     db.commit()
> except Exception as e:
>     # Sin rollback, la sesión tiene el nombre cambiado pendiente
>     # La próxima operación podría commitarlo accidentalmente
>     db.rollback()  # Limpia todos los cambios pendientes
>     raise
> ```

```python
# db.add()       - Añadir a sesión
# db.commit()    - Guardar cambios
# db.rollback()  - Deshacer cambios
# db.refresh()   - Actualizar objeto con datos de DB
```

> **Resumen de operaciones de sesión:**
>
> | Método | Qué hace | Cuándo usar |
> |--------|----------|-------------|
> | `db.add(obj)` | Añade objeto a sesión (pendiente) | Al crear nuevo registro |
> | `db.commit()` | Persiste cambios en BD | Al finalizar operación |
> | `db.rollback()` | Descarta cambios pendientes | En caso de error |
> | `db.refresh(obj)` | Recarga objeto desde BD | Después de commit para obtener valores generados |
> | `db.delete(obj)` | Marca objeto para eliminación | Al eliminar |
> | `db.flush()` | Envía cambios a BD sin commit | Para obtener IDs antes de commit |

## Autenticación

```python
def autenticar_usuario(db: Session, email: str, password: str):
    """
    Autentica un usuario.

    Returns:
        Usuario si las credenciales son correctas
        None si son incorrectas
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return None

    if not verify_password(password, usuario.contraseña_hash):
        return None

    return usuario
```

> **¿Por qué devolver `None` en lugar de lanzar excepción?**
>
> **Con excepción:**
>
> ```python
> def autenticar_usuario(db: Session, email: str, password: str):
>     usuario = db.query(Usuario).filter(Usuario.email == email).first()
>     if not usuario:
>         raise ValueError("Usuario no encontrado")
>     if not verify_password(password, usuario.contraseña_hash):
>         raise ValueError("Contraseña incorrecta")
>     return usuario
>
> # En el router
> try:
>     usuario = autenticar_usuario(db, email, password)
> except ValueError as e:
>     raise HTTPException(401, str(e))
> ```
>
> **Problema de seguridad:**
> - Mensaje diferente para usuario no encontrado vs contraseña incorrecta
> - Permite **enumeración de usuarios**: un atacante puede saber qué emails existen
>
> **Con `None`:**
>
> ```python
> def autenticar_usuario(db: Session, email: str, password: str):
>     usuario = db.query(Usuario).filter(Usuario.email == email).first()
>     if not usuario:
>         return None
>     if not verify_password(password, usuario.contraseña_hash):
>         return None
>     return usuario
>
> # En el router
> usuario = autenticar_usuario(db, email, password)
> if not usuario:
>     raise HTTPException(401, "Credenciales incorrectas")  # Mensaje genérico
> ```
>
> **Beneficio:**
> - Mismo mensaje sea usuario no encontrado o contraseña incorrecta
> - No permite enumeración de usuarios

> **¿Por qué usar constantes de tiempo en verificación de contraseña?**
>
> ```python
> # Implementación correcta
> if not verify_password(password, usuario.contraseña_hash):
>     return None
>
> # Implementación incorrecta (¡NO HACER!)
> if not usuario:
>     return None  # Rápido
> if password == usuario.contraseña_hash:  # Comparación directa
>     return usuario
> return None
> ```
>
> **Ataque de timing:**
> - Si el código toma diferente tiempo según si el usuario existe, un atacante puede medir el tiempo de respuesta
> - `verify_password` de bcrypt usa **comparación de tiempo constante**
> - Mantiene el mismo tiempo de respuesta sin importar el resultado

## Manejo de Errores

### En el servicio

```python
def crear_usuario(db: Session, datos: UsuarioCreate):
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")
    # ...
```

### En el router

```python
from fastapi import HTTPException

@router.post("/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

> **¿Por qué `ValueError` en servicios y `HTTPException` en routers?**
>
> **Principio: Servicios no conocen HTTP**
>
> Los servicios deben ser agnósticos al contexto:
> - Pueden usarse desde API REST
> - Pueden usarse desde CLI
> - Pueden usarse desde tests
>
> ```python
> # Servicio - excepciones genéricas
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     if email_existe:
>         raise ValueError("Email ya registrado")  # Genérico
>
> # Router - traduce a HTTP
> @router.post("/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     try:
>         return crear_usuario(db, datos)
>     except ValueError as e:
>         raise HTTPException(400, str(e))  # HTTP específico
>
> # CLI - traduce a salida de consola
> def crear_usuario_cli():
>     try:
>         crear_usuario(db, datos)
>     except ValueError as e:
>         print(f"Error: {e}")  # Consola
> ```

### Códigos HTTP

| Código | Uso |
|--------|-----|
| 200 | GET, PUT exitoso |
| 201 | POST exitoso |
| 204 | DELETE exitoso |
| 400 | Datos inválidos |
| 401 | No autenticado |
| 403 | Sin permisos |
| 404 | No encontrado |
| 409 | Conflicto |
| 500 | Error del servidor |

> **¿Cuándo usar cada código?**
>
> | Código | Cuándo usar | Ejemplo |
> |--------|-------------|---------|
> | **200 OK** | Operación exitosa con respuesta | GET /usuarios, PUT /usuarios/1 |
> | **201 Created** | Recurso creado exitosamente | POST /usuarios → nuevo usuario |
> | **204 No Content** | Operación exitosa sin respuesta | DELETE /usuarios/1 |
> | **400 Bad Request** | Datos de entrada inválidos | Email con formato incorrecto |
> | **401 Unauthorized** | No hay token de autenticación | Acceder a /me sin token |
> | **403 Forbidden** | Autenticado pero sin permisos | Usuario normal intentando borrar liga |
> | **404 Not Found** | Recurso no existe | GET /usuarios/999 |
> | **409 Conflict** | Conflicto con estado actual | Email ya registrado |
> | **422 Unprocessable Entity** | Error de validación Pydantic | Schema inválido |
> | **500 Internal Server Error** | Error inesperado del servidor | Excepción no manejada |
>
> **Patrones comunes:**
>
> ```python
> # Crear - 201
> @router.post("/", status_code=201)
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     return crear_usuario(db, datos)
>
> # Eliminar - 204
> @router.delete("/{id}", status_code=204)
> def eliminar(id: int, db: Session = Depends(get_db)):
>     eliminar_usuario(db, id)
>     return None  # Sin contenido
>
> # No encontrado - 404
> @router.get("/{id}")
> def obtener(id: int, db: Session = Depends(get_db)):
>     usuario = obtener_usuario_por_id(db, id)
>     if not usuario:
>         raise HTTPException(404, "Usuario no encontrado")
>     return usuario
>
> # Conflicto - 409
> @router.post("/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     try:
>         return crear_usuario(db, datos)
>     except ValueError as e:
>         if "ya registrado" in str(e):
>             raise HTTPException(409, str(e))
>         raise HTTPException(400, str(e))
> ```

## Buenas Prácticas

### Un servicio por recurso

```
services/
├── usuario_service.py
├── liga_service.py
├── equipo_service.py
└── ...
```

> **¿Por qué no un archivo gigante?**
>
> **Todo en un archivo:**
>
> ```python
> # services.py - 2000 líneas
> def crear_usuario(...): ...
> def obtener_usuario(...): ...
> def crear_liga(...): ...
> def obtener_liga(...): ...
> # ... muchas más funciones
> ```
>
> **Problemas:**
> - Difícil de encontrar código
> - Conflictos en Git
> - Difícil de testear
>
> **Un archivo por recurso:**
>
> ```python
> # usuario_service.py - Solo funciones de usuario
> def crear_usuario(...): ...
> def obtener_usuario(...): ...
> def actualizar_usuario(...): ...
> def eliminar_usuario(...): ...
> ```
>
> **Ventajas:**
> - Fácil localizar: "Funciones de usuario" → `usuario_service.py`
> - Cambios aislados: Modificar usuarios no afecta ligas
> - Tests organizados: `test_usuario_service.py`

### Funciones específicas

```python
# ✅ Correcto
def crear_usuario(db: Session, datos: UsuarioCreate):
    pass

# ❌ Evitar
def crear_usuario_y_enviar_email_y_log(db, datos):
    pass
```

> **¿Por qué funciones específicas?**
>
> **Principio de Responsabilidad Única (SRP):**
>
> Cada función debe tener una sola razón para cambiar.
>
> ```python
> # ❌ Múltiples responsabilidades
> def crear_usuario_y_enviar_email_y_log(db, datos):
>     # Crear usuario
>     usuario = Usuario(...)
>     db.add(usuario)
>     db.commit()
>
>     # Enviar email
>     send_email(usuario.email, "Bienvenido")
>
>     # Log
>     log_event("usuario_creado", usuario.id)
>
> # Problema: Si cambia el email, el log o el usuario, esta función cambia
> ```
>
> ```python
> # ✅ Responsabilidades separadas
> def crear_usuario(db: Session, datos: UsuarioCreate):
>     usuario = Usuario(...)
>     db.add(usuario)
>     db.commit()
>     return usuario
>
> def enviar_email_bienvenida(usuario: Usuario):
>     send_email(usuario.email, "Bienvenido")
>
> def log_usuario_creado(usuario: Usuario):
>     log_event("usuario_creado", usuario.id)
>
> # En el router
> @router.post("/")
> def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
>     usuario = crear_usuario(db, datos)
>     enviar_email_bienvenida(usuario)
>     log_usuario_creado(usuario)
>     return usuario
> ```
>
> **Ventajas:**
> - Cada función tiene una razón para cambiar
> - Fácil de testear individualmente
> - Fácil de reutilizar

### Nombres descriptivos

```python
# ✅ Correcto
def obtener_usuario_por_email(db: Session, email: str):
    pass

# ❌ Evitar
def get_user(db, e):
    pass
```

> **¿Por qué nombres descriptivos?**
>
> **Código legible vs críptico:**
>
> ```python
> # ❌ Nombres cortos pero confusos
> def get_user(db, e):
>     u = db.query(User).filter(User.email == e).first()
>     return u
>
> # ✅ Nombres descriptivos
> def obtener_usuario_por_email(db: Session, email: str):
>     usuario = db.query(Usuario).filter(Usuario.email == email).first()
>     return usuario
> ```
>
> **El código se lee más veces de las que se escribe:**
>
> - Escribes una vez
> - Lees 10 veces (por ti y otros desarrolladores)
> - El tiempo ahorrado escribiendo nombres cortos se pierde leyendo después
>
> **Convenciones del proyecto:**
>
> | Operación | Prefijo | Ejemplo |
> |-----------|---------|---------|
> | Crear | `crear_` | `crear_usuario` |
> | Obtener uno | `obtener_` | `obtener_usuario_por_id` |
> | Obtener varios | `listar_` | `listar_usuarios` |
> | Actualizar | `actualizar_` | `actualizar_usuario` |
> | Eliminar | `eliminar_` | `eliminar_usuario` |
> | Verificar | `verificar_` | `verificar_email_unico` |
> | Contar | `contar_` | `contar_usuarios_activos` |

### Documentar con docstrings

```python
def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario en el sistema.

    Args:
        db: Sesión de base de datos SQLAlchemy
        datos: Datos validados del usuario

    Returns:
        Usuario: Objeto creado con ID asignado

    Raises:
        ValueError: Si el email ya está registrado
    """
```

> **¿Por qué docstrings?**
>
> **Sin documentación:**
>
> ```python
> def crear_usuario(db, datos):
>     # ¿Qué hace?
>     # ¿Qué devuelve?
>     # ¿Qué errores puede lanzar?
> ```
>
> **Con documentación:**
>
> ```python
> def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
>     """
>     Crea un nuevo usuario en el sistema.
>
>     Args:
>         db: Sesión de base de datos SQLAlchemy
>         datos: Datos validados del usuario

>         Returns:
>         Usuario: Objeto creado con ID asignado

>         Raises:
>         ValueError: Si el email ya está registrado
>         """
> ```
>
> **Beneficios:**
>
> 1. **Autodocumentación**: IDEs muestran la documentación al pasar el cursor
> 2. **Intellisense**: Autocompletado muestra parámetros y retorno
> 3. **Mantenimiento**: Futuros desarrolladores entienden el código
> 4. **Generación de docs**: Herramientas como Sphinx pueden generar documentación
>
> **Formato estándar (Google style):**
>
> ```python
> def funcion(param1: tipo, param2: tipo) -> tipo_retorno:
>     """
>     Descripción breve de la función.
>
>     Descripción más detallada si es necesaria.
>
>     Args:
>         param1: Descripción del parámetro 1.
>         param2: Descripción del parámetro 2.

>         Returns:
>         Descripción de lo que devuelve.

>         Raises:
>         TipoExcepcion: Cuándo se lanza esta excepción.

>         Example:
>         >>> funcion("valor1", "valor2")
>         "resultado"
>     """
> ```