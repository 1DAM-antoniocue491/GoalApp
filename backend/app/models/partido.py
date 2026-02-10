# app/models/partido.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from database.connection import Base

class Partido(Base):
    __tablename__ = "partidos"

    id_partido = Column(Integer, primary_key=True, index=True)

    id_liga = Column(Integer, ForeignKey("ligas.id_liga"), nullable=False)
    id_equipo_local = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    id_equipo_visitante = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)

    fecha = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String(50), nullable=False)

    goles_local = Column(Integer, nullable=True)
    goles_visitante = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
