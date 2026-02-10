from pydantic import BaseModel
from datetime import datetime

class UsuarioRolBase(BaseModel):
    id_usuario: int
    id_rol: int

class UsuarioRolCreate(UsuarioRolBase):
    pass

class UsuarioRolUpdate(BaseModel):
    id_usuario: int | None = None
    id_rol: int | None = None

class UsuarioRolResponse(BaseModel):
    id_usuario_rol: int
    id_usuario: int
    id_rol: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
