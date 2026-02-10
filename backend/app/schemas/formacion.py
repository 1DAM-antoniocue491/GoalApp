from pydantic import BaseModel, Field
from datetime import datetime

class FormacionBase(BaseModel):
    nombre: str = Field(..., max_length=20)

class FormacionCreate(FormacionBase):
    pass

class FormacionUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=20)

class FormacionResponse(BaseModel):
    id_formacion: int
    nombre: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
