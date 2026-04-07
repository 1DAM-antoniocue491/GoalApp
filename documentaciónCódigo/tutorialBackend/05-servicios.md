# Servicios: La Lógica de Negocio (Para Principiantes)

## ¿Qué es un Servicio?

Imagina el restaurante otra vez:

```
┌─────────────────────────────────────────────┐
│                MESERO (Router)              │
│   "Hola, ¿qué desea ordenar?"              │
│   Recibe el pedido y lo pasa a la cocina   │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│               COCINA (Servicio)             │
│   "Entendido, voy a preparar esto."        │
│   Aplica las reglas y prepara la comida     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│               DESPENSA (Modelo)             │
│   "El tomate está en la nevera."           │
│   Guarda y busca los ingredientes           │
└─────────────────────────────────────────────┘
```

**El servicio es la cocina:** recibe los ingredientes, aplica las reglas, y prepara el resultado.

---

## ¿Por qué Separar la Lógica?

### Sin Servicio (❌ Lógica en el Router)

```python
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # ❌ Todo mezclado en el router

    # Verificar que el email no exista
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(400, "Email ya registrado")

    # Hashear la contraseña
    hashed = bcrypt.hash(datos.password)

    # Crear el usuario
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hashed
    )

    # Guardar
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario
```

**Problemas:**

1. **Mezclado:** HTTP y lógica de negocio en el mismo lugar
2. **Difícil de probar:** Necesitas hacer peticiones HTTP para probar
3. **No reutilizable:** ¿Qué si quieres crear usuarios desde un script?
4. **Largo y confuso:** Demasiado código en un solo lugar

### Con Servicio (✅ Separado)

```python
# Router (solo HTTP)
@router.post("/usuarios/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(db, datos)
    except ValueError as e:
        raise HTTPException(400, str(e))

# Service (solo lógica)
def crear_usuario(db: Session, datos: UsuarioCreate):
    # Verificar email único
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise ValueError("El email ya está registrado")

    # Hashear contraseña
    hashed = hash_password(datos.password)

    # Crear usuario
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hashed
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario
```

**Ventajas:**

| Ventaja | Descripción |
|---------|-------------|
| **Limpio** | Router solo maneja HTTP, Service solo lógica |
| **Reutilizable** | Usar desde REST API, CLI, tests |
| **Fácil de probar** | No necesitas peticiones HTTP |
| **Organizado** | Cada cosa en su lugar |

---

## Estructura de un Servicio

### Archivo Típico

```python
# app/api/services/usuario_service.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

# Configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones auxiliares (privadas)
def hash_password(password: str) -> str:
    """Genera un hash de la contraseña."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(password, hashed)

# Funciones principales (públicas)
def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """Crea un nuevo usuario."""
    pass

def obtener_usuario_por_id(db: Session, id_usuario: int) -> Usuario | None:
    """Obtiene un usuario por su ID."""
    pass

def obtener_usuario_por_email(db: Session, email: str) -> Usuario | None:
    """Obtiene un usuario por su email."""
    pass

def actualizar_usuario(db: Session, id_usuario: int, datos: UsuarioUpdate) -> Usuario:
    """Actualiza un usuario."""
    pass

def eliminar_usuario(db: Session, id_usuario: int) -> None:
    """Elimina un usuario."""
    pass
```

### Organización

| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Crear | `crear_` | `crear_usuario` |
| Obtener uno | `obtener_..._por_` | `obtener_usuario_por_id` |
| Obtener varios | `listar_` | `listar_usuarios` |
| Actualizar | `actualizar_` | `actualizar_usuario` |
| Eliminar | `eliminar_` | `eliminar_usuario` |
| Verificar | `verificar_` | `verificar_email_unico` |
| Contar | `contar_` | `contar_usuarios_activos` |

---

## Operaciones CRUD

### Crear (CREATE)

```python
def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario.

    Pasos:
    1. Verificar que el email no exista
    2. Hashear la contraseña
    3. Crear el objeto
    4. Guardar en la base de datos
    5. Refrescar para obtener el ID
    """
    # 1. Verificar email único
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    # 2. Hashear contraseña
    contraseña_hash = hash_password(datos.password)

    # 3. Crear objeto
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=contraseña_hash
    )

    # 4. Guardar
    db.add(usuario)      # Agregar a la sesión (en memoria)
    db.commit()          # Guardar en la base de datos
    db.refresh(usuario)  # Obtener el ID generado

    # 5. Devolver
    return usuario
```

**¿Por qué verificar email antes del INSERT?**

```python
# Sin verificación:
db.add(usuario)
db.commit()  # ERROR: IntegrityError si el email ya existe
# El usuario ve un error genérico de base de datos

# Con verificación:
if db.query(Usuario).filter(Usuario.email == datos.email).first():
    raise ValueError("El email ya está registrado")
# El usuario ve un mensaje claro
```

**¿Por qué `db.add()` → `db.commit()` → `db.refresh()`?**

```python
usuario = Usuario(nombre="Juan", email="juan@email.com")

db.add(usuario)       # Agregar a la sesión (en memoria, NO en BD)
print(usuario.id_usuario)  # None - todavía no tiene ID

db.commit()           # Guardar en la base de datos
print(usuario.id_usuario)  # Puede tener ID (depende del driver)

db.refresh(usuario)   # Recargar desde la base de datos
print(usuario.id_usuario)  # Definitivamente tiene ID
print(usuario.created_at)  # También tiene created_at
```

### Leer (READ)

```python
def obtener_usuario_por_id(db: Session, id_usuario: int) -> Usuario | None:
    """Obtiene un usuario por su ID."""
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

def obtener_usuario_por_email(db: Session, email: str) -> Usuario | None:
    """Obtiene un usuario por su email."""
    return db.query(Usuario).filter(Usuario.email == email).first()

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    """Lista todos los usuarios con paginación."""
    return db.query(Usuario).offset(skip).limit(limit).all()

def contar_usuarios(db: Session) -> int:
    """Cuenta el total de usuarios."""
    return db.query(func.count(Usuario.id_usuario)).scalar()
```

**¿Por qué funciones separadas?**

```python
# ❌ Una función con parámetros opcionales
def buscar_usuario(db: Session, id: int = None, email: str = None):
    query = db.query(Usuario)
    if id:
        query = query.filter(Usuario.id_usuario == id)
    if email:
        query = query.filter(Usuario.email == email)
    return query.first()

# ¿Qué devuelve? ¿Usuario? ¿Lista? ¿Qué parámetros son obligatorios?
usuario = buscar_usuario(db, id=1)       # ¿Qué pasa?
usuario = buscar_usuario(db, email="x")  # ¿Y esto?
usuario = buscar_usuario(db)             # ¿Sin parámetros?

# ✅ Funciones separadas
usuario = obtener_usuario_por_id(db, 1)      # Claro: obtiene por ID
usuario = obtener_usuario_por_email(db, "x") # Claro: obtiene por email
usuarios = listar_usuarios(db)              # Claro: lista todos
```

**¿Por qué `first()` y no `all()` o `one()`?**

| Método | Cuándo usar | Si no encuentra |
|--------|------------|-----------------|
| `first()` | Esperas 0 o 1 | Devuelve `None` |
| `one()` | Esperas exactamente 1 | Lanza excepción |
| `all()` | Esperas varios | Devuelve `[]` |

```python
# Para buscar por ID (0 o 1 resultado)
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()
if usuario is None:
    raise ValueError("Usuario no encontrado")

# Para buscar por email único (0 o 1 resultado)
usuario = db.query(Usuario).filter(Usuario.email == email).first()

# Para listar (múltiples resultados)
usuarios = db.query(Usuario).all()
```

### Actualizar (UPDATE)

```python
def actualizar_usuario(db: Session, id_usuario: int, datos: UsuarioUpdate) -> Usuario:
    """
    Actualiza un usuario existente.

    Pasos:
    1. Buscar el usuario
    2. Actualizar solo los campos proporcionados
    3. Guardar cambios
    """
    # 1. Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise ValueError("Usuario no encontrado")

    # 2. Actualizar solo los campos proporcionados
    if datos.nombre is not None:
        usuario.nombre = datos.nombre

    if datos.email is not None:
        # Verificar que el email no esté en uso por otro usuario
        existente = db.query(Usuario).filter(
            Usuario.email == datos.email,
            Usuario.id_usuario != id_usuario  # Excluirse a sí mismo
        ).first()
        if existente:
            raise ValueError("El email ya está en uso")
        usuario.email = datos.email

    if datos.telefono is not None:
        usuario.telefono = datos.telefono

    # 3. Guardar
    db.commit()
    db.refresh(usuario)

    return usuario
```

**¿Por qué verificar `is not None`?**

```python
# ❌ Sin verificación
def actualizar_usuario(db, id, datos):
    usuario = obtener_usuario(db, id)
    usuario.nombre = datos.nombre    # Si datos.nombre es None, ¡borra el nombre!
    usuario.email = datos.email      # Si datos.email es None, ¡borra el email!
    db.commit()

# ✅ Con verificación
def actualizar_usuario(db, id, datos):
    usuario = obtener_usuario(db, id)
    if datos.nombre is not None:
        usuario.nombre = datos.nombre  # Solo actualiza si se proporcionó
    if datos.email is not None:
        usuario.email = datos.email   # Solo actualiza si se proporcionó
    db.commit()
```

**¿Por qué excluirse a sí mismo en la verificación de email?**

```python
# Usuario con ID 1 tiene email "juan@email.com"
# Quiere actualizar su nombre pero no cambiar el email

# Sin excluirse a sí mismo:
existente = db.query(Usuario).filter(Usuario.email == "juan@email.com").first()
# existente es el mismo usuario!
if existente:
    raise ValueError("Email ya en uso")  # ❌ Error incorrecto

# Con excluirse a sí mismo:
existente = db.query(Usuario).filter(
    Usuario.email == "juan@email.com",
    Usuario.id_usuario != 1  # Excluir al usuario actual
).first()
# existente es None, OK continuar
```

### Eliminar (DELETE)

```python
def eliminar_usuario(db: Session, id_usuario: int) -> None:
    """
    Elimina un usuario.

    Pasos:
    1. Buscar el usuario
    2. Eliminar
    """
    # 1. Buscar
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise ValueError("Usuario no encontrado")

    # 2. Eliminar
    db.delete(usuario)
    db.commit()
```

**¿Qué pasa con las relaciones?**

```python
# Si el usuario tiene roles y eliminas el usuario...
usuario = db.query(Usuario).first()
db.delete(usuario)
db.commit()  # ERROR: foreign key constraint!

# Solución 1: CASCADE (eliminar en cascada)
class Usuario(Base):
    roles = relationship("Rol", secondary="usuario_rol", cascade="delete")

# Solución 2: Eliminar relaciones primero
db.query(UsuarioRol).filter(UsuarioRol.id_usuario == usuario.id_usuario).delete()
db.delete(usuario)
db.commit()

# Solución 3: Soft delete (no eliminar, solo marcar)
class Usuario(Base):
    activo = Column(Boolean, default=True)

def eliminar_usuario(db, id_usuario):
    usuario = obtener_usuario(db, id_usuario)
    usuario.activo = False  # No eliminar, solo marcar
    db.commit()
```

---

## Consultas con SQLAlchemy

### Consultas Básicas

```python
# Obtener todos
usuarios = db.query(Usuario).all()

# Obtener uno por ID
usuario = db.query(Usuario).filter(Usuario.id_usuario == 1).first()

# Obtener uno por campo único
usuario = db.query(Usuario).filter(Usuario.email == "juan@email.com").first()

# Filtrar con condiciones
usuarios_activos = db.query(Usuario).filter(Usuario.activo == True).all()

# Filtrar con LIKE (búsqueda parcial)
usuarios = db.query(Usuario).filter(Usuario.nombre.like("%Juan%")).all()

# Ordenar
usuarios = db.query(Usuario).order_by(Usuario.nombre).all()
usuarios = db.query(Usuario).order_by(desc(Usuario.created_at)).all()

# Paginación
usuarios = db.query(Usuario).offset(0).limit(10).all()   # Página 1
usuarios = db.query(Usuario).offset(10).limit(10).all()  # Página 2
```

### Consultas con JOIN

```python
from sqlalchemy.orm import joinedload

# Cargar usuario con sus roles
usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()

for usuario in usuarios:
    print(usuario.roles)  # Ya están cargados, no hace query adicional
```

**El problema N+1:**

```python
# Sin joinedload
usuarios = db.query(Usuario).all()  # 1 query

for usuario in usuarios:
    print(usuario.roles)  # N queries adicionales!

# Si hay 100 usuarios = 101 queries en total

# Con joinedload
usuarios = db.query(Usuario).options(joinedload(Usuario.roles)).all()

for usuario in usuarios:
    print(usuario.roles)  # Ya cargados, 0 queries adicionales

# Total: 1 query con JOIN
```

### Agregaciones

```python
from sqlalchemy import func

# Contar
total = db.query(func.count(Usuario.id_usuario)).scalar()

# Promedio
promedio_edad = db.query(func.avg(Usuario.edad)).scalar()

# Máximo
max_edad = db.query(func.max(Usuario.edad)).scalar()

# Suma
total_salarios = db.query(func.sum(Usuario.salario)).scalar()

# Contar con filtro
activos = db.query(func.count(Usuario.id_usuario)).filter(
    Usuario.activo == True
).scalar()

# Agrupar
from sqlalchemy import func

# Contar usuarios por rol
resultados = db.query(
    Rol.nombre,
    func.count(Usuario.id_usuario)
).join(Usuario.roles).group_by(Rol.nombre).all()

# Resultado: [("admin", 5), ("editor", 10), ("viewer", 50)]
```

---

## Transacciones

### ¿Qué es una Transacción?

Una transacción es un **conjunto de operaciones que se ejecutan todas o ninguna**:

```
┌─────────────────────────────────────────────────────┐
│                  TRANSACCIÓN                        │
├─────────────────────────────────────────────────────┤
│  1. Sacar $100 de Juan                              │
│  2. Poner $100 en María                             │
│                                                      │
│  Si todo OK → commit (guardar todo)                 │
│  Si hay error → rollback (deshacer todo)           │
└─────────────────────────────────────────────────────┘
```

### Sin Transacción (❌)

```python
# Transferir puntos
def transferir_puntos(db, de_id, a_id, puntos):
    # 1. Sacar puntos
    usuario_origen = db.query(Usuario).filter(Usuario.id_usuario == de_id).first()
    usuario_origen.puntos -= puntos
    db.commit()  # ¡Guardado!

    # ERROR AQUÍ → Los puntos se fueron pero María no recibió nada
    raise Exception("Algo salió mal")

    # 2. Poner puntos
    usuario_destino = db.query(Usuario).filter(Usuario.id_usuario == a_id).first()
    usuario_destino.puntos += puntos
    db.commit()

# Resultado: Juan perdió $100, María no recibió nada
```

### Con Transacción (✅)

```python
def transferir_puntos(db, de_id, a_id, puntos):
    try:
        # 1. Sacar puntos
        usuario_origen = db.query(Usuario).filter(Usuario.id_usuario == de_id).first()
        usuario_origen.puntos -= puntos

        # 2. Poner puntos
        usuario_destino = db.query(Usuario).filter(Usuario.id_usuario == a_id).first()
        usuario_destino.puntos += puntos

        # 3. Guardar todo junto
        db.commit()

    except Exception as e:
        # Si hay error, deshacer todo
        db.rollback()
        raise e
```

**En SQLAlchemy, con `autocommit=False`, las transacciones son automáticas:**

```python
# Todo esto está en una transacción
usuario_origen.puntos -= puntos  # En memoria, no guardado
usuario_destino.puntos += puntos  # En memoria, no guardado
db.commit()  # ¡Ahora sí se guarda todo!
```

---

## Autenticación

### Verificar Usuario

```python
def autenticar_usuario(db: Session, email: str, password: str) -> Usuario | None:
    """
    Verifica si las credenciales son correctas.

    Devuelve el usuario si es correcto, None si no.
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

**¿Por qué devolver `None` y no lanzar error?**

```python
# ❌ Con error específico
def autenticar_usuario(db, email, password):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise ValueError("Usuario no encontrado")  # Error específico
    if not verify_password(password, usuario.contraseña_hash):
        raise ValueError("Contraseña incorrecta")  # Error específico

# Problema: Un atacante puede saber si un email existe
# Si recibe "Usuario no encontrado", sabe que el email NO existe
# Si recibe "Contraseña incorrecta", sabe que el email SÍ existe
# Esto se llama "enumeración de usuarios"

# ✅ Con None
def autenticar_usuario(db, email, password):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None  # Email no encontrado
    if not verify_password(password, usuario.contraseña_hash):
        return None  # Contraseña incorrecta
    return usuario

# En el router:
usuario = autenticar_usuario(db, email, password)
if not usuario:
    raise HTTPException(401, "Credenciales incorrectas")  # Mensaje genérico
```

---

## Manejo de Errores

### En el Servicio

```python
def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    # Verificar email único
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise ValueError("El email ya está registrado")

    # Crear usuario
    usuario = Usuario(...)
    db.add(usuario)
    db.commit()
    return usuario
```

**¿Por qué `ValueError` y no `HTTPException`?**

```python
# ❌ HTTPException en el servicio
def crear_usuario(db, datos):
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(400, "Email ya existe")  # Conoce HTTP

# Problema: El servicio está acoplado a FastAPI/HTTP
# No puedes usar este servicio desde:
# - Un script CLI
# - Otro framework
# - Tests unitarios sin mockear HTTP

# ✅ ValueError en el servicio
def crear_usuario(db, datos):
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise ValueError("Email ya existe")  # Genérico

# En el router (HTTP)
@router.post("/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(db, datos)
    except ValueError as e:
        raise HTTPException(400, str(e))  # Traducir a HTTP

# En un script CLI
try:
    crear_usuario(db, datos)
except ValueError as e:
    print(f"Error: {e}")  # Traducir a consola
```

---

## Buenas Prácticas

### Un Archivo por Recurso

```python
# ❌ Todo en un archivo
# services.py (2000 líneas)
def crear_usuario(...): ...
def crear_liga(...): ...
def crear_equipo(...): ...

# ✅ Un archivo por recurso
# services/usuario_service.py
def crear_usuario(...): ...
def obtener_usuario(...): ...
def actualizar_usuario(...): ...
```

### Funciones Específicas

```python
# ❌ Función que hace muchas cosas
def crear_usuario_y_enviar_email_y_log(db, datos):
    usuario = Usuario(...)
    db.add(usuario)
    db.commit()
    send_email(usuario.email, "Bienvenido")
    log_event("usuario_creado", usuario.id)

# ✅ Funciones separadas
def crear_usuario(db, datos):
    usuario = Usuario(...)
    db.add(usuario)
    db.commit()
    return usuario

def enviar_email_bienvenida(usuario):
    send_email(usuario.email, "Bienvenido")

# En el router
@router.post("/")
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = crear_usuario(db, datos)
    enviar_email_bienvenida(usuario)
    return usuario
```

### Nombres Descriptivos

```python
# ❌ Nombres confusos
def get_user(db, e):
    u = db.query(User).filter(User.email == e).first()
    return u

# ✅ Nombres claros
def obtener_usuario_por_email(db: Session, email: str) -> Usuario | None:
    """Obtiene un usuario por su email."""
    return db.query(Usuario).filter(Usuario.email == email).first()
```

### Documentar con Docstrings

```python
def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario en el sistema.

    Args:
        db: Sesión de base de datos SQLAlchemy.
        datos: Datos validados del usuario.

    Returns:
        Usuario: El usuario creado con su ID asignado.

    Raises:
        ValueError: Si el email ya está registrado.

    Example:
        >>> usuario = crear_usuario(db, UsuarioCreate(
        ...     nombre="Juan",
        ...     email="juan@email.com",
        ...     password="mi_contraseña"
        ... ))
        >>> print(usuario.id_usuario)
        1
    """
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
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

---

## Resumen

Aprendiste:

1. **Servicio** = La cocina donde se prepara la lógica
2. **Separación** = Router solo HTTP, Service solo lógica
3. **CRUD** = Create, Read, Update, Delete con funciones separadas
4. **Consultas** = SQLAlchemy para buscar datos
5. **Transacciones** = Operaciones que se ejecutan todas o ninguna
6. **Errores** = ValueError en service, HTTPException en router
7. **Buenas prácticas** = Un archivo por recurso, funciones específicas

**¿Listo para el siguiente paso?**

Ve a **06-routers.md** para aprender cómo crear los endpoints HTTP.