"""
Schemas de validación para el recurso Liga.
Define los modelos Pydantic para request/response de la API relacionados con ligas de fútbol.
"""
from pydantic import BaseModel, Field
from datetime import datetime

class LigaBase(BaseModel):
    """
    Schema base de Liga con campos comunes.
    Usado como clase base para herencia.
    
    Attributes:
        nombre (str): Nombre de la liga (máximo 100 caracteres)
        temporada (str): Temporada de la liga (ej: 2024-2025, máximo 20 caracteres)
    """
    nombre: str = Field(..., max_length=100)
    temporada: str = Field(..., max_length=20)

class LigaCreate(LigaBase):
    """
    Schema para crear una nueva liga.
    Usado en el endpoint POST /ligas/
    Hereda todos los campos de LigaBase como requeridos.
    """
    pass

class LigaUpdate(BaseModel):
    """
    Schema para actualizar una liga existente.
    Usado en el endpoint PUT/PATCH /ligas/{id_liga}
    
    Attributes:
        nombre (str | None): Nombre de la liga (máximo 100 caracteres)
        temporada (str | None): Temporada de la liga (ej: 2024-2025, máximo 20 caracteres)
    """
    nombre: str | None = Field(None, max_length=100)
    temporada: str | None = Field(None, max_length=20)

class LigaResponse(BaseModel):
    """
    Schema de respuesta para una liga.
    Usado en las respuestas de los endpoints GET /ligas/
    
    Attributes:
        id_liga (int): Identificador único de la liga
        nombre (str): Nombre de la liga
        temporada (str): Temporada de la liga (ej: 2024-2025)
        created_at (datetime): Fecha y hora de creación del registro
        updated_at (datetime): Fecha y hora de última actualización del registro
    """
    id_liga: int
    nombre: str
    temporada: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Permite crear el schema desde objetos ORM de SQLAlchemy
