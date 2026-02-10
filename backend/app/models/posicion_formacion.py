# app/models/posicion_formacion.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from database.connection import Base

class PosicionFormacion(Base):
    __tablename__ = "posiciones_formacion"

    id_posicion = Column(Integer, primary_key=True, index=True)
    id_formacion = Column(Integer, ForeignKey("formaciones.id_formacion"), nullable=False)

    nombre = Column(String(50), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
