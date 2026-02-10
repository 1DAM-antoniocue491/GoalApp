from pydantic import BaseModel, Field
from datetime import datetime

class EquipoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    escudo: str | None = Field(None, max_length=255)
    colores: str | None = Field(None, max_length=50)
    id_liga: int
    id_entrenador: int
    id_delegado: int

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    escudo: str | None = Field(None, max_length=255)
    colores: str | None = Field(None, max_length=50)
    id_liga: int | None = None
    id_entrenador: int | None = None
    id_delegado: int | None = None

class EquipoResponse(BaseModel):
    id_equipo: int
    nombre: str
    escudo: str | None
    colores: str | None
    id_liga: int
    id_entrenador: int
    id_delegado: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
