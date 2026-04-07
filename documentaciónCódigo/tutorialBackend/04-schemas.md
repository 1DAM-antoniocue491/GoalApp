# Schemas: Validación de Datos (Para Principiantes)

## ¿Qué es un Schema?

Imagina que estás en un restaurante y quieres hacer un pedido. El mesero te da un **formulario**:

```
┌─────────────────────────────────────────────────────────┐
│                 FORMULARIO DE PEDIDO                     │
├─────────────────────────────────────────────────────────┤
│  Nombre: _____________________                           │
│                                                          │
│  Email: _____________________ (debe ser un email válido) │
│                                                          │
│  Teléfono: ________________ (opcional)                   │
│                                                          │
│  [ ] Acepto los términos y condiciones                   │
│                                                          │
│  [ENVIAR]                                                │
└─────────────────────────────────────────────────────────┘
```

**Un schema es igual:** es un formulario que verifica que los datos estén correctos antes de procesarlos.

---

## ¿Por qué Necesitamos Schemas?

### El Problema

Imagina que recibes estos datos del frontend:

```json
{
  "nombre": "Juan",
  "email": "esto-no-es-un-email",
  "edad": "veinticinco",
  "telefono": 123456789
}
```

**¿Qué está mal?**

- El email no es válido
- La edad debería ser número, no texto
- El teléfono debería ser string, no número

Sin validación, estos datos entrarían a tu base de datos y causarían problemas.

### La Solución: Pydantic

**Pydantic** es una librería que valida los datos **automáticamente**:

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str                    # Obligatorio, debe ser texto
    email: EmailStr                # Obligatorio, debe ser email válido
    edad: int                      # Obligatorio, debe ser número
    telefono: Optional[str] = None # Opcional, puede ser None
```

```python
# Datos incorrectos
datos = {
    "nombre": "Juan",
    "email": "esto-no-es-un-email",  # ❌ Email inválido
    "edad": "veinticinco",            # ❌ Texto en lugar de número
    "telefono": 123456789             # ❌ Número en lugar de texto
}

usuario = UsuarioCreate(**datos)  # ¡Pydantic lanza error automático!
# Error: email debe ser un email válido
# Error: edad debe ser un número
```

```python
# Datos correctos
datos = {
    "nombre": "Juan",
    "email": "juan@email.com",
    "edad": 25,
    "telefono": "123456789"
}

usuario = UsuarioCreate(**datos)  # ✅ Todo correcto
print(usuario.nombre)   # "Juan"
print(usuario.email)    # "juan@email.com"
```

---

## Tipos de Schemas

### ¿Por qué tener varios schemas?

**Imagina el ciclo de vida de un usuario:**

1. **Crear usuario:** Necesito `nombre`, `email`, `password`
2. **Actualizar usuario:** Necesito `nombre`, `email` (opcionales), pero NO `password`
3. **Responder al cliente:** Devuelvo `id`, `nombre`, `email`, pero NO `password`

**Si usas un solo schema para todo:**

```python
# ❌ Un solo schema para todo (problemático)
class Usuario(BaseModel):
    id_usuario: int      # Solo para responder
    nombre: str
    email: EmailStr
    password: str        # Solo para crear
    contraseña_hash: str # Nunca se devuelve
    created_at: datetime # Solo para responder
```

**Problemas:**

- ¿Qué campos son obligatorios al crear?
- ¿Devuelvo la contraseña al cliente? (¡PELIGRO!)
- ¿Puedo actualizar el ID? (¡NO!)

### La Solución: Schemas Separados

```python
# Para CREAR usuario
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

# Para ACTUALIZAR usuario
class UsuarioUpdate(BaseModel):
    nombre: str | None = None       # Opcional
    email: EmailStr | None = None   # Opcional

# Para RESPONDER al cliente
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    created_at: datetime
    # ¡Sin password! Seguridad primero
```

**Uso:**

```python
# Crear usuario
@router.post("/usuarios/", response_model=UsuarioResponse)
def crear(datos: UsuarioCreate):
    # datos.nombre ✅
    # datos.email ✅
    # datos.password ✅
    # datos.id_usuario ❌ No existe
    ...

# Actualizar usuario
@router.put("/usuarios/{id}", response_model=UsuarioResponse)
def actualizar(id: int, datos: UsuarioUpdate):
    # datos.nombre ✅ Puede venir o no
    # datos.email ✅ Puede venir o no
    # datos.password ❌ No existe
    ...

# Obtener usuario
@router.get("/usuarios/{id}", response_model=UsuarioResponse)
def obtener(id: int):
    usuario = ...
    # Devuelve: {id_usuario, nombre, email, created_at}
    # ¡NUNCA devuelve password!
    return usuario
```

---

## Crear Schemas

### Schema Base (Para Reutilizar)

Muchos campos se repiten en varios schemas. Podemos crear un **schema base**:

```python
class UsuarioBase(BaseModel):
    """Campos comunes para crear y actualizar."""
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
```

```python
# Heredar del base
class UsuarioCreate(UsuarioBase):
    """Para crear usuario."""
    password: str = Field(..., min_length=6)

class UsuarioResponse(UsuarioBase):
    """Para responder al cliente."""
    id_usuario: int
    created_at: datetime

    class Config:
        from_attributes = True  # Para leer de SQLAlchemy
```

**¿Por qué usar herencia?**

| Sin herencia (❌) | Con herencia (✅) |
|------------------|------------------|
| Código repetido | Código reutilizado |
| Si cambias un campo, cambias en varios lados | Cambias solo en el base |
| Fácil cometer errores | Consistencia garantizada |

### Validaciones con Field

`Field` te permite agregar reglas a los campos:

```python
from pydantic import BaseModel, Field

class UsuarioCreate(BaseModel):
    # Obligatorio, entre 2 y 100 caracteres
    nombre: str = Field(..., min_length=2, max_length=100)

    # Obligatorio, debe ser positivo, máximo 150
    edad: int = Field(..., gt=0, le=150)

    # Obligatorio, mayor que 0
    salario: float = Field(..., gt=0)

    # Opcional, máximo 20 caracteres
    telefono: str | None = Field(None, max_length=20)

    # Con descripción y ejemplo
    email: EmailStr = Field(
        ...,
        description="Email del usuario",
        examples=["juan@email.com", "maria@gmail.com"]
    )
```

**Validaciones disponibles:**

| Validación | Significado | Ejemplo |
|------------|-------------|---------|
| `...` | Obligatorio | `Field(...)` |
| `gt=n` | Mayor que n | `gt=0` → mayor que 0 |
| `ge=n` | Mayor o igual que n | `ge=0` → 0 o más |
| `lt=n` | Menor que n | `lt=100` → menos de 100 |
| `le=n` | Menor o igual que n | `le=100` → 100 o menos |
| `min_length=n` | Longitud mínima | `min_length=2` |
| `max_length=n` | Longitud máxima | `max_length=100` |
| `pattern=r"..."` | Expresión regular | `pattern=r"^\d+$"` → solo números |

### Validadores Personalizados

A veces necesitas reglas especiales:

```python
from pydantic import BaseModel, field_validator
import re

class UsuarioCreate(BaseModel):
    nombre: str
    telefono: str | None = None

    @field_validator("telefono")
    def validar_telefono(cls, v: str | None) -> str | None:
        """Valida que el teléfono tenga formato correcto."""
        if v is None:
            return v

        # Quitar espacios y guiones
        telefono_limpio = re.sub(r"[\s\-]", "", v)

        # Validar formato: +34 123 456 789 o 123456789
        if not re.match(r"^(\+\d{1,3})?\d{6,14}$", telefono_limpio):
            raise ValueError("Formato de teléfono inválido")

        return telefono_limpio
```

```python
# Pruebas
datos = {"nombre": "Juan", "telefono": "+34 123 456 789"}
usuario = UsuarioCreate(**datos)  # ✅ Válido

datos = {"nombre": "Juan", "telefono": "abc"}  # ❌ Error: formato inválido
```

### Validador de Modelo (Múltiples Campos)

```python
from pydantic import BaseModel, model_validator

class UsuarioCreate(BaseModel):
    password: str
    confirmar_password: str

    @model_validator(mode="after")
    def validar_passwords_iguales(self):
        """Verifica que las contraseñas coincidan."""
        if self.password != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
```

```python
# Pruebas
datos = {"password": "123456", "confirmar_password": "123456"}
usuario = UsuarioCreate(**datos)  # ✅ Válido

datos = {"password": "123456", "confirmar_password": "654321"}  # ❌ Error
```

---

## Tipos de Datos en Pydantic

### Tipos Básicos

```python
from pydantic import BaseModel
from datetime import datetime, date
from typing import List

class Ejemplo(BaseModel):
    # Texto
    nombre: str

    # Números
    edad: int
    precio: float

    # Booleano
    activo: bool = True

    # Fechas
    fecha_nacimiento: date          # Solo fecha (2024-01-15)
    creado_en: datetime              # Fecha y hora (2024-01-15 10:30:00)

    # Listas
    tags: List[str] = []

    # Opcionales
    descripcion: str | None = None
```

### Tipos Especiales

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from uuid import UUID

class Ejemplo(BaseModel):
    # Email (valida que sea un email real)
    email: EmailStr

    # URL (valida que sea una URL real)
    web: HttpUrl

    # UUID (identificador único)
    id: UUID
```

```python
# Ejemplos
datos = {
    "email": "juan@email.com",   # ✅ Válido
    "web": "https://ejemplo.com", # ✅ Válido
    "id": "550e8400-e29b-41d4-a716-446655440000"  # ✅ Válido
}
```

### Enums (Valores Fijos)

```python
from pydantic import BaseModel
from enum import Enum

class GeneroEnum(str, Enum):
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"

class UsuarioCreate(BaseModel):
    nombre: str
    genero: GeneroEnum
```

```python
# ✅ Válido
datos = {"nombre": "Juan", "genero": "masculino"}
usuario = UsuarioCreate(**datos)

# ❌ Error: "indefinido" no está en el enum
datos = {"nombre": "Juan", "genero": "indefinido"}
usuario = UsuarioCreate(**datos)
```

---

## `from_attributes = True`

### ¿Qué hace esta configuración?

```python
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr

    class Config:
        from_attributes = True
```

**Sin `from_attributes = True`:**

```python
# Obtener de la base de datos
usuario_db = db.query(Usuario).first()  # Objeto SQLAlchemy

# ❌ Intentar crear schema
usuario_response = UsuarioResponse.model_validate(usuario_db)
# Error: Input should be a valid dictionary
```

**Con `from_attributes = True`:**

```python
# Obtener de la base de datos
usuario_db = db.query(Usuario).first()  # Objeto SQLAlchemy

# ✅ Crear schema
usuario_response = UsuarioResponse.model_validate(usuario_db)
# Funciona: Pydantic lee los atributos del objeto
```

**¿Qué hace exactamente?**

Pydantic puede leer de dos tipos de datos:

1. **Diccionarios** (`dict`) - Siempre funciona
2. **Objetos con atributos** (SQLAlchemy) - Necesita `from_attributes = True`

```python
# Sin from_attributes
UsuarioResponse(nombre="Juan")  # ✅ Diccionario funciona
UsuarioResponse(usuario_db)     # ❌ Objeto no funciona

# Con from_attributes
UsuarioResponse(nombre="Juan")  # ✅ Diccionario funciona
UsuarioResponse(usuario_db)     # ✅ Objeto también funciona
```

---

## Errores Automáticos

### ¿Qué pasa si los datos son incorrectos?

Pydantic devuelve errores claros automáticamente:

```python
# Datos incorrectos
datos = {
    "nombre": "Ju",           # ❌ Mínimo 2 caracteres
    "email": "no-es-email",   # ❌ No es email
    "edad": -5                 # ❌ Debe ser positivo
}

usuario = UsuarioCreate(**datos)
```

**Respuesta de error:**

```json
{
    "detail": [
        {
            "loc": ["body", "nombre"],
            "msg": "String should have at least 2 characters",
            "type": "string_too_short"
        },
        {
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email"
        },
        {
            "loc": ["body", "edad"],
            "msg": "Input should be greater than 0",
            "type": "greater_than"
        }
    ]
}
```

**Código HTTP: 422 Unprocessable Entity**

---

## Uso en Routers

### `response_model`

```python
@router.post("/usuarios/", response_model=UsuarioResponse)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = crear_usuario(db, datos)
    return usuario
```

**¿Qué hace `response_model`?**

1. **Filtra campos:** Solo devuelve los campos de `UsuarioResponse`
2. **Valida la respuesta:** Verifica que los datos sean correctos
3. **Convierte tipos:** Convierte automáticamente (ej: datetime → string)
4. **Documenta:** Swagger muestra el schema de respuesta

**Ejemplo de filtrado:**

```python
# El modelo tiene estos campos:
class Usuario(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    password: str           # ❌ No debería devolverse
    contraseña_hash: str    # ❌ No debería devolverse
    created_at: datetime

# El schema de respuesta:
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    created_at: datetime
    # Sin password ni contraseña_hash

# Con response_model=UsuarioResponse:
# La respuesta FILTRA automáticamente:
{
    "id_usuario": 1,
    "nombre": "Juan",
    "email": "juan@email.com",
    "created_at": "2024-01-15T10:30:00"
    # password y contraseña_hash NO aparecen
}
```

### Ejemplo Completo

```python
# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from enum import Enum

class GeneroEnum(str, Enum):
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"

# Schema base (campos comunes)
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

# Para crear usuario
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)
    genero: GeneroEnum | None = None
    fecha_nacimiento: date | None = None

# Para actualizar usuario
class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = None
    telefono: str | None = None

# Para responder
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    genero: GeneroEnum | None = None
    telefono: str | None = None
    fecha_nacimiento: date | None = None
    created_at: datetime

    class Config:
        from_attributes = True

# Para lista de usuarios
class UsuarioListResponse(BaseModel):
    total: int
    usuarios: list[UsuarioResponse]
```

```python
# app/api/routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.api.services.usuario_service import crear_usuario, obtener_usuarios
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioListResponse

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario."""
    try:
        usuario = crear_usuario(db, datos)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=UsuarioListResponse)
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos los usuarios."""
    usuarios = obtener_usuarios(db, skip=skip, limit=limit)
    total = contar_usuarios(db)
    return {"total": total, "usuarios": usuarios}

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener(id_usuario: int, db: Session = Depends(get_db)):
    """Obtiene un usuario por ID."""
    usuario = obtener_usuario_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
```

---

## Relaciones en Schemas

### ¿Cómo representar relaciones?

```python
# Un equipo pertenece a una liga
class EquipoResponse(BaseModel):
    id_equipo: int
    nombre: str
    id_liga: int  # La FK

    class Config:
        from_attributes = True

# Una liga tiene muchos equipos
class LigaResponse(BaseModel):
    id_liga: int
    nombre: str
    equipos: list[EquipoResponse] = []  # Lista de equipos

    class Config:
        from_attributes = True
```

### El Problema de las Referencias Circulares

```python
# ❌ Esto causa error
class EquipoResponse(BaseModel):
    liga: LigaResponse  # LigaResponse no existe todavía

class LigaResponse(BaseModel):
    equipos: list[EquipoResponse]  # EquipoResponse no existe todavía
```

**Solución: Usar strings**

```python
# ✅ Esto funciona
class EquipoResponse(BaseModel):
    liga: "LigaResponse"  # String, no clase

class LigaResponse(BaseModel):
    equipos: list[EquipoResponse]

# Después de definir ambos, reconstruir
EquipoResponse.model_rebuild()
```

**Solución alternativa: `from __future__ import annotations`**

```python
from __future__ import annotations  # Al inicio del archivo

class EquipoResponse(BaseModel):
    liga: LigaResponse  # Ahora funciona como string

class LigaResponse(BaseModel):
    equipos: list[EquipoResponse]
```

---

## Resumen

Aprendiste:

1. **Schema** = Un formulario que valida los datos
2. **Pydantic** = La librería que valida automáticamente
3. **Schemas separados** = Diferentes formularios para crear, actualizar, responder
4. **Validaciones** = Reglas para verificar los datos (Field, field_validator)
5. **Tipos especiales** = EmailStr, HttpUrl, Enum
6. **`from_attributes = True`** = Para leer de objetos SQLAlchemy
7. **`response_model`** = Filtra y documenta las respuestas

**¿Listo para el siguiente paso?**

Ve a **05-servicios.md** para aprender cómo escribir la lógica de negocio.