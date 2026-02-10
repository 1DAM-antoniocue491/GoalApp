from pydantic import BaseModel, Field
from datetime import datetime

class NotificacionBase(BaseModel):
    id_usuario: int
    mensaje: str
    leida: bool = False

class NotificacionCreate(NotificacionBase):
    pass

class NotificacionUpdate(BaseModel):
    id_usuario: int | None = None
    mensaje: str | None = None
    leida: bool | None = None

class NotificacionResponse(BaseModel):
    id_notificacion: int
    id_usuario: int
    mensaje: str
    leida: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
