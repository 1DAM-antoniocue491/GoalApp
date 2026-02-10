# app/models/notificacion.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Text
from database.connection import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
