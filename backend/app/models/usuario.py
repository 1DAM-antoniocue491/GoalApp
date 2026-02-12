# app/models/usuario.py
"""
Modelo de Usuario para la base de datos.
Representa los usuarios registrados en el sistema con sus credenciales y datos básicos.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from ..database.connection import Base


class Usuario(Base):
    """
    Modelo ORM para la tabla 'usuarios'.
    
    Un usuario puede tener múltiples roles (Admin, Coach, Delegate, Player, Viewer)
    y puede estar asociado a equipos como jugador, entrenador o delegado.
    
    Attributes:
        id_usuario (int): Identificador único del usuario (Primary Key)
        nombre (str): Nombre completo del usuario (máx. 100 caracteres)
        email (str): Correo electrónico único del usuario (máx. 100 caracteres)
        contraseña_hash (str): Hash bcrypt de la contraseña (máx. 255 caracteres)
        created_at (datetime): Fecha y hora de creación del registro
        updated_at (datetime): Fecha y hora de última actualización
    """
    __tablename__ = "usuarios"

    # Clave primaria
    id_usuario = Column(Integer, primary_key=True, index=True)
    
    # Información básica
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)  # Email único para login
    contraseña_hash = Column(String(255), nullable=False)  # Almacenado con bcrypt

    # Auditoría: fechas de creación y actualización
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
