# app/models/rol.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database.connection import Base

class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
