from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.schemas.notificacion import NotificacionResponse
from app.api.services.notificacion_service import (
    obtener_notificaciones_usuario,
    marcar_notificacion_leida
)

router = APIRouter(
    prefix="/notificaciones",
    tags=["Notificaciones"]
)

@router.get("/", response_model=list[NotificacionResponse])
def listar_notificaciones(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obtener_notificaciones_usuario(db, current_user.id_usuario)

@router.put("/{notificacion_id}")
def marcar_leida(
    notificacion_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    marcar_notificacion_leida(db, notificacion_id, current_user.id_usuario)
    return {"mensaje": "Notificación marcada como leída"}
