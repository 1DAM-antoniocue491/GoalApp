from pydantic import BaseModel
from datetime import datetime

class FormacionEquipoBase(BaseModel):
    id_equipo: int
    id_formacion: int

class FormacionEquipoCreate(FormacionEquipoBase):
    pass

class FormacionEquipoUpdate(BaseModel):
    id_equipo: int | None = None
    id_formacion: int | None = None

class FormacionEquipoResponse(BaseModel):
    id_formacion_equipo: int
    id_equipo: int
    id_formacion: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
