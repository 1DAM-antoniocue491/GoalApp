from sqlalchemy.orm import Session
from app.models.formacion import Formacion
from app.models.posicion_formacion import PosicionFormacion
from app.schemas.formacion import FormacionCreate, PosicionCreate

def crear_formacion(db: Session, datos: FormacionCreate):
    formacion = Formacion(nombre=datos.nombre)
    db.add(formacion)
    db.commit()
    db.refresh(formacion)
    return formacion

def obtener_formaciones(db: Session):
    return db.query(Formacion).all()

def crear_posicion(db: Session, datos: PosicionCreate):
    posicion = PosicionFormacion(
        id_formacion=datos.id_formacion,
        nombre=datos.nombre
    )
    db.add(posicion)
    db.commit()
    db.refresh(posicion)
    return posicion

def obtener_posiciones(db: Session, formacion_id: int):
    return db.query(PosicionFormacion).filter(PosicionFormacion.id_formacion == formacion_id).all()
