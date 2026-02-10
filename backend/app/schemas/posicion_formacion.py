from pydantic import BaseModel, Field
from datetime import datetime

class PosicionFormacionBase(BaseModel):
    id_formacion: int
    nombre: str = Field(..., max_length=50)

class PosicionFormacionCreate(PosicionFormacionBase):
    pass

class PosicionFormacionUpdate(BaseModel):
    id_formacion: int | None = None
    nombre: str | None = Field(None, max_length=50)

class PosicionFormacionResponse(BaseModel):
    id_posicion: int
    id_formacion: int
    nombre: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
