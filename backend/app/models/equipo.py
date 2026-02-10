# app/models/equipo.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from database.connection import Base

class Equipo(Base):
    __tablename__ = "equipos"

    id_equipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    escudo = Column(String(255), nullable=True)
    colores = Column(String(50), nullable=True)

    id_liga = Column(Integer, ForeignKey("ligas.id_liga"), nullable=False)
    id_entrenador = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_delegado = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
