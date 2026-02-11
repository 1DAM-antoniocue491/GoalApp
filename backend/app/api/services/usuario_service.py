from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================
# UTILIDADES
# ============================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ============================================================
# AUTENTICACIÓN
# ============================================================

def autenticar_usuario(db: Session, email: str, password: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    if not verify_password(password, usuario.contraseña_hash):
        return None
    return usuario

# ============================================================
# CRUD USUARIOS
# ============================================================

def crear_usuario(db: Session, datos: UsuarioCreate):
    # Verificar email único
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
    return db.query(Usuario).all()

def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()

def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioUpdate):
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    if datos.nombre is not None:
        usuario.nombre = datos.nombre

    if datos.email is not None:
        # Verificar email único
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

def eliminar_usuario(db: Session, usuario_id: int):
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    db.delete(usuario)
    db.commit()

# ============================================================
# ROLES
# ============================================================

def asignar_rol_a_usuario(db: Session, usuario_id: int, rol_id: int):
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    rol = db.query(Rol).filter(Rol.id_rol == rol_id).first()
    if not rol:
        raise ValueError("Rol no encontrado")

    # Evitar duplicados
    existente = db.query(UsuarioRol).filter(
        UsuarioRol.id_usuario == usuario_id,
        UsuarioRol.id_rol == rol_id
    ).first()

    if existente:
        raise ValueError("El usuario ya tiene este rol")

    asignacion = UsuarioRol(id_usuario=usuario_id, id_rol=rol_id)
    db.add(asignacion)
    db.commit()
    return True
