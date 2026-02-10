from pydantic import BaseModel
from datetime import datetime

class FormacionPartidoBase(BaseModel):
    id_partido: int
    id_equipo: int
    id_formacion: int

class FormacionPartidoCreate(FormacionPartidoBase):
    pass

class FormacionPartidoUpdate(BaseModel):
    id_partido: int | None = None
    id_equipo: int | None = None
    id_formacion: int | None = None

class FormacionPartidoResponse(BaseModel):
    id_formacion_partido: int
    id_partido: int
    id_equipo: int
    id_formacion: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
