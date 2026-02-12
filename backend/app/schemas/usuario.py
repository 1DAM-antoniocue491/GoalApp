"""
Schemas de validación para el recurso Usuario.
Define los modelos Pydantic para request/response de la API relacionados con usuarios del sistema.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UsuarioBase(BaseModel):
    """
    Schema base de Usuario con campos comunes.
    Usado como clase base para herencia.
    
    Attributes:
        nombre (str): Nombre completo del usuario (máximo 100 caracteres)
        email (EmailStr): Correo electrónico válido del usuario
    """
    nombre: str = Field(..., max_length=100)
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    """
    Schema para crear un nuevo usuario.
    Usado en el endpoint POST /usuarios/
    
    Attributes:
        nombre (str): Nombre completo del usuario (máximo 100 caracteres)
        email (EmailStr): Correo electrónico válido del usuario
        contraseña (str): Contraseña en texto plano (mínimo 6 caracteres, se hasheará en el servidor)
    """
    contraseña: str = Field(..., min_length=6)  # Se almacenará como hash en la base de datos

class UsuarioUpdate(BaseModel):
    """
    Schema para actualizar un usuario existente.
    Usado en el endpoint PUT/PATCH /usuarios/{id_usuario}
    
    Attributes:
        nombre (str | None): Nombre completo del usuario (máximo 100 caracteres)
        email (EmailStr | None): Correo electrónico válido del usuario
        contraseña (str | None): Nueva contraseña en texto plano (mínimo 6 caracteres, se hasheará en el servidor)
    """
    nombre: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    contraseña: str | None = Field(None, min_length=6)  # Se almacenará como hash en la base de datos

class UsuarioResponse(BaseModel):
    """
    Schema de respuesta para un usuario.
    Usado en las respuestas de los endpoints GET /usuarios/
    
    Attributes:
        id_usuario (int): Identificador único del usuario
        nombre (str): Nombre completo del usuario
        email (EmailStr): Correo electrónico del usuario
        created_at (datetime): Fecha y hora de creación del registro
        updated_at (datetime): Fecha y hora de última actualización del registro
    """
    id_usuario: int
    nombre: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Permite crear el schema desde objetos ORM de SQLAlchemy
