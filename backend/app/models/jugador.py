# app/models/jugador.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from database.connection import Base

class Jugador(Base):
    __tablename__ = "jugadores"

    id_jugador = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)
    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)

    posicion = Column(String(50), nullable=False)
    dorsal = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
