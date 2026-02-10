from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class EstadoPartido(str, Enum):
    programado = "programado"
    en_juego = "en_juego"
    finalizado = "finalizado"
    cancelado = "cancelado"

class PartidoBase(BaseModel):
    id_liga: int
    id_equipo_local: int
    id_equipo_visitante: int
    fecha: datetime
    estado: EstadoPartido
    goles_local: int | None = None
    goles_visitante: int | None = None

class PartidoCreate(PartidoBase):
    pass

class PartidoUpdate(BaseModel):
    id_liga: int | None = None
    id_equipo_local: int | None = None
    id_equipo_visitante: int | None = None
    fecha: datetime | None = None
    estado: EstadoPartido | None = None
    goles_local: int | None = None
    goles_visitante: int | None = None

class PartidoResponse(BaseModel):
    id_partido: int
    id_liga: int
    id_equipo_local: int
    id_equipo_visitante: int
    fecha: datetime
    estado: EstadoPartido
    goles_local: int | None
    goles_visitante: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
