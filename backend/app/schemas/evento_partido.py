from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TipoEvento(str, Enum):
    gol = "gol"
    tarjeta_amarilla = "tarjeta_amarilla"
    tarjeta_roja = "tarjeta_roja"
    cambio = "cambio"
    mvp = "mvp"

class EventoPartidoBase(BaseModel):
    id_partido: int
    id_jugador: int
    tipo_evento: TipoEvento
    minuto: int = Field(..., ge=1, le=120)

class EventoPartidoCreate(EventoPartidoBase):
    pass

class EventoPartidoUpdate(BaseModel):
    id_partido: int | None = None
    id_jugador: int | None = None
    tipo_evento: TipoEvento | None = None
    minuto: int | None = Field(None, ge=1, le=120)

class EventoPartidoResponse(BaseModel):
    id_evento: int
    id_partido: int
    id_jugador: int
    tipo_evento: TipoEvento
    minuto: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
