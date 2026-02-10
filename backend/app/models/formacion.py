# app/models/formacion.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database.connection import Base

class Formacion(Base):
    __tablename__ = "formaciones"

    id_formacion = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(20), nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
