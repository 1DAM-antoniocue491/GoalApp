from pydantic import BaseModel, Field
from datetime import datetime

class JugadorBase(BaseModel):
    id_usuario: int
    id_equipo: int
    posicion: str = Field(..., max_length=50)
    dorsal: int = Field(..., ge=1, le=99)
    activo: bool = True

class JugadorCreate(JugadorBase):
    pass

class JugadorUpdate(BaseModel):
    id_usuario: int | None = None
    id_equipo: int | None = None
    posicion: str | None = Field(None, max_length=50)
    dorsal: int | None = Field(None, ge=1, le=99)
    activo: bool | None = None

class JugadorResponse(BaseModel):
    id_jugador: int
    id_usuario: int
    id_equipo: int
    posicion: str
    dorsal: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
