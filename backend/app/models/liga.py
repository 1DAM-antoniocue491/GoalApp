# app/models/liga.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database.connection import Base

class Liga(Base):
    __tablename__ = "ligas"

    id_liga = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    temporada = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
