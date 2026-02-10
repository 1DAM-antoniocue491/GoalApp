# app/models/usuario_rol.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from database.connection import Base

class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    id_usuario_rol = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
