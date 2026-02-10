from pydantic import BaseModel, Field
from datetime import datetime

class LigaBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    temporada: str = Field(..., max_length=20)

class LigaCreate(LigaBase):
    pass

class LigaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    temporada: str | None = Field(None, max_length=20)

class LigaResponse(BaseModel):
    id_liga: int
    nombre: str
    temporada: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
