from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    contraseña: str = Field(..., min_length=6)

class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    contraseña: str | None = Field(None, min_length=6)

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
