from pydantic import BaseModel, Field
from datetime import datetime

class RolBase(BaseModel):
    nombre: str = Field(..., max_length=50)
    descripcion: str | None = Field(None, max_length=255)

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=50)
    descripcion: str | None = Field(None, max_length=255)

class RolResponse(BaseModel):
    id_rol: int
    nombre: str
    descripcion: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
