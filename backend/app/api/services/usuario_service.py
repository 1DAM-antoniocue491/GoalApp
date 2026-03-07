"""
Servicios de lógica de negocio para Usuario.
Maneja operaciones CRUD de usuarios, autenticación, gestión de contraseñas
con hashing bcrypt, y asignación de roles.
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

# Configuración del contexto de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================
# UTILIDADES
# ============================================================


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de una contraseña usando bcrypt.
    
    Args:
        password (str): Contraseña en texto plano
    
    Returns:
        str: Hash de la contraseña
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        password (str): Contraseña en texto plano a verificar
        hashed (str): Hash almacenado de la contraseña
    
    Returns:
        bool: True si la contraseña es correcta, False en caso contrario
    """
    return pwd_context.verify(password, hashed)

# ============================================================
# AUTENTICACIÓN
# ============================================================


def autenticar_usuario(db: Session, email: str, password: str):
    """
    Autentica un usuario mediante email y contraseña.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        email (str): Email del usuario
        password (str): Contraseña en texto plano
    
    Returns:
        Usuario: Objeto Usuario si las credenciales son correctas, None en caso contrario
    """
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    # Verificar contraseña
    if not verify_password(password, usuario.contraseña_hash):
        return None
    return usuario

# ============================================================
# CRUD USUARIOS
# ============================================================


def crear_usuario(db: Session, datos: UsuarioCreate):
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        datos (UsuarioCreate): Datos del usuario (nombre, email, contraseña)
    
    Returns:
        Usuario: Objeto Usuario creado con su ID asignado
    
    Raises:
        ValueError: Si el email ya está registrado
    """
    # Verificar que el email sea único
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        contraseña_hash=hash_password(datos.contraseña)
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def obtener_usuarios(db: Session):
    """
    Obtiene todos los usuarios registrados.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
    
    Returns:
        list[Usuario]: Lista con todos los usuarios
    """
    return db.query(Usuario).all()


def obtener_usuario_por_id(db: Session, usuario_id: int):
    """
    Busca un usuario por su ID.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        usuario_id (int): ID del usuario a buscar
    
    Returns:
        Usuario: Objeto Usuario si existe, None si no se encuentra
    """
    return db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()


def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate):
    """
    Actualiza los datos de un usuario existente.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        usuario_id (int): ID del usuario a actualizar
        datos (UsuarioUpdate): Datos a actualizar (nombre, email y/o contraseña)
    
    Returns:
        Usuario: Objeto Usuario actualizado
    
    Raises:
        ValueError: Si el usuario no existe o el email ya está en uso
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    if datos.nombre is not None:
        usuario.nombre = datos.nombre

    if datos.email is not None:
        # Verificar que el nuevo email sea único (excluyendo el usuario actual)
        existente = db.query(Usuario).filter(
            Usuario.email == datos.email,
            Usuario.id_usuario != usuario_id
        ).first()
        if existente:
            raise ValueError("El email ya está en uso")
        usuario.email = datos.email

    if datos.contraseña is not None:
        # Hashear la nueva contraseña
        usuario.contraseña_hash = hash_password(datos.contraseña)

    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int):
    """
    Elimina un usuario del sistema.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        usuario_id (int): ID del usuario a eliminar
    
    Raises:
        ValueError: Si el usuario no existe
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    db.delete(usuario)
    db.commit()

# ============================================================
# ROLES
# ============================================================


def asignar_rol_a_usuario(db: Session, usuario_id: int, rol_id: int):
    """
    Asigna un rol a un usuario.
    
    Args:
        db (Session): Sesión de base de datos SQLAlchemy
        usuario_id (int): ID del usuario
        rol_id (int): ID del rol a asignar
    
    Returns:
        bool: True si se asignó correctamente
    
    Raises:
        ValueError: Si el usuario o rol no existe, o si el usuario ya tiene ese rol
    """
    # Verificar que el usuario existe
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    # Verificar que el rol existe
    rol = db.query(Rol).filter(Rol.id_rol == rol_id).first()
    if not rol:
        raise ValueError("Rol no encontrado")

    # Evitar asignaciones duplicadas
    existente = db.query(UsuarioRol).filter(
        UsuarioRol.id_usuario == usuario_id,
        UsuarioRol.id_rol == rol_id
    ).first()

    if existente:
        raise ValueError("El usuario ya tiene este rol")

    # Crear la asignación
    asignacion = UsuarioRol(id_usuario=usuario_id, id_rol=rol_id)
    db.add(asignacion)
    db.commit()
    return True
