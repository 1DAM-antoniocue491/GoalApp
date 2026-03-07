"""
Schemas de validación para el recurso Usuario.
Define los modelos Pydantic para request/response de la API relacionados con usuarios del sistema.
"""
from pydantic import BaseModel, EmailStr, Field, validator
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
    password: str = Field(
        ...,
        min_length=6,                # longitud mínima que tú quieras
        alias="contraseña",          # permite que el JSON use "contraseña"
    )
    # --------------------------------------------------------------
    # Validador personalizado de Pydantic.
    # Se ejecuta automáticamente después de que los campos básicos
    # hayan sido validados (tipo, longitud mínima, etc.).
    # --------------------------------------------------------------
    @validator("contraseña")
    def validar_longitud_maxima(cls, v: str) -> str:
        """
        bcrypt solo permite contraseñas de **≤ 72 bytes**.
        Este método verifica que la cadena codificada en UTF‑8 no supere
        ese límite. Si la supera, lanzamos un `ValueError`; FastAPI
        transformará esa excepción en una respuesta HTTP 422 con el
        mensaje correspondiente.
        """
        max_bytes = 72                     # Límite impuesto por bcrypt
        # Convertimos la cadena a bytes para contar el número real de bytes.
        # Los caracteres multibyte (por ejemplo, emojis) pueden ocupar
        # más de un byte, por eso usamos `encode('utf-8')`.
        if len(v.encode("utf-8")) > max_bytes:
            raise ValueError(
                f"La contraseña no puede superar los {max_bytes} bytes "
                "(≈ 72 caracteres ASCII)."
            )
        # Si todo está bien, devolvemos la contraseña tal cual.
        return v
    
    class Config:
        # Con esta opción el modelo acepta **ambos** nombres:
        #   - "password"
        #   - "contraseña"
        allow_population_by_field_name = True

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
        from_attributes = True  # Permite crear el schema desde objetos ORM de SQLAlchemy
