# app/models/formacion_equipo.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from database.connection import Base

class FormacionEquipo(Base):
    __tablename__ = "formacion_equipo"

    id_formacion_equipo = Column(Integer, primary_key=True, index=True)

    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    id_formacion = Column(Integer, ForeignKey("formaciones.id_formacion"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
