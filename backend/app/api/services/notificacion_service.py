from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion

def obtener_notificaciones_usuario(db: Session, usuario_id: int):
    return db.query(Notificacion).filter(Notificacion.id_usuario == usuario_id).all()

def marcar_notificacion_leida(db: Session, notificacion_id: int, usuario_id: int):
    notificacion = db.query(Notificacion).filter(
        Notificacion.id_notificacion == notificacion_id,
        Notificacion.id_usuario == usuario_id
    ).first()

    if not notificacion:
        raise ValueError("Notificación no encontrada")

    notificacion.leida = True
    db.commit()
    return True
