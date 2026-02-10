# app/models/evento_partido.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from database.connection import Base

class EventoPartido(Base):
    __tablename__ = "eventos_partido"

    id_evento = Column(Integer, primary_key=True, index=True)

    id_partido = Column(Integer, ForeignKey("partidos.id_partido"), nullable=False)
    id_jugador = Column(Integer, ForeignKey("jugadores.id_jugador"), nullable=False)

    tipo_evento = Column(String(50), nullable=False)
    minuto = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
