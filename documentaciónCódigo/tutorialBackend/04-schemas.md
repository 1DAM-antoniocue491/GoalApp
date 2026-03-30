# Schemas (Validación)

## Pydantic

Pydantic valida datos automáticamente y genera documentación:

```
JSON entrada → Pydantic Schema → Objeto Python validado
{"edad": "25"}                    {"edad": 25}
```

> **¿Por qué Pydantic y no validación manual?**
>
> **Sin Pydantic (validación manual):**
>
> ```python
> @router.post("/usuarios/")
> def crear(datos: dict):
>     # Validación manual - propenso a errores
>     if "nombre" not in datos:
>         raise HTTPException(400, "nombre requerido")
>     if len(datos["nombre"]) > 100:
>         raise HTTPException(400, "nombre muy largo")
>     if "email" not in datos:
>         raise HTTPException(400, "email requerido")
>     if "@" not in datos["email"]:
>         raise HTTPException(400, "email inválido")
>     # ... más validaciones
>     # Código repetitivo y difícil de mantener
> ```
>
> **Con Pydantic:**
>
> ```python
> class UsuarioCreate(BaseModel):
>     nombre: str = Field(..., max_length=100)
>     email: EmailStr  # Valida formato automáticamente
>
> @router.post("/usuarios/")
> def crear(datos: UsuarioCreate):  # Validación automática
>     # datos.nombre ya está validado y tipado
>     # Si falla, Pydantic devuelve 422 con detalles
> ```
>
> **Ventajas de Pydantic:**
>
> 1. **Validación automática**: Tipos, rangos, formatos.
> 2. **Conversión de tipos**: `"25"` → `25` automáticamente.
> 3. **Documentación automática**: Swagger usa los schemas.
> 4. **Errores claros**: Mensajes de error estructurados.
> 5. **IDE friendly**: Autocompletado y type checking.

## Tipos de Schemas

| Schema | Propósito | Uso |
|--------|-----------|-----|
| `Base` | Campos comunes | Herencia |
| `Create` | Datos para crear | POST |
| `Update` | Datos para actualizar | PUT/PATCH |
| `Response` | Datos de respuesta | GET |

> **¿Por qué separar en múltiples schemas?**
>
> **Problema si usamos un solo schema:**
>
> ```python
> # ❌ Un schema para todo
> class Usuario(BaseModel):
>     id_usuario: int        # Solo en respuesta
>     nombre: str
>     email: EmailStr
>     password: str          # Solo en creación
>     contraseña_hash: str   # Solo interno, nunca en respuesta
>     created_at: datetime   # Solo en respuesta
>
> @router.post("/usuarios/")
> def crear(datos: Usuario):
>     # Problema: ¿qué campos son obligatorios?
>     # Problema: ¿qué campos se ignoran?
>     # Problema: ¿se devuelve password en la respuesta?
> ```
>
> **Con schemas separados:**
>
> ```python
> # ✅ Schemas separados por propósito
> class UsuarioCreate(BaseModel):
>     nombre: str            # Obligatorio en creación
>     email: EmailStr        # Obligatorio en creación
>     password: str          # Obligatorio en creación
>
> class UsuarioUpdate(BaseModel):
>     nombre: str | None = None      # Opcional en actualización
>     email: EmailStr | None = None  # Opcional en actualización
>     # Sin password - no se actualiza aquí
>
> class UsuarioResponse(BaseModel):
>     id_usuario: int        # Solo lectura
>     nombre: str
>     email: EmailStr
>     created_at: datetime
>     # Sin password ni hash
>
> @router.post("/", response_model=UsuarioResponse)
> def crear(datos: UsuarioCreate):
>     # Solo acepta nombre, email, password
>
> @router.put("/{id}", response_model=UsuarioResponse)
> def actualizar(id: int, datos: UsuarioUpdate):
>     # Solo acepta nombre, email (opcionales)
> ```
>
> **Beneficios de separar:**
>
> | Beneficio | Descripción |
> |-----------|-------------|
> | Seguridad | `password` nunca aparece en respuesta |
> | Claridad | Cada endpoint tiene sus campos documentados |
> | Validación | Diferentes reglas por operación |
> | Swagger | Documentación precisa por endpoint |

## Estructura de Schemas

### Schema Base

```python
# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from enum import Enum
import re

class GeneroEnum(str, Enum):
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"

class UsuarioBase(BaseModel):
    """Campos comunes para crear y actualizar."""
    nombre: str = Field(..., max_length=100)
    email: EmailStr
```

> **¿Por qué usar un schema Base?**
>
> **Sin Base (código repetido):**
>
> ```python
> class UsuarioCreate(BaseModel):
>     nombre: str = Field(..., max_length=100)
>     email: EmailStr
>
> class UsuarioUpdate(BaseModel):
>     nombre: str | None = Field(None, max_length=100)  # Mismo campo
>     email: EmailStr | None = None                      # Mismo campo
>
> class UsuarioResponse(BaseModel):
>     nombre: str                    # Mismo campo
>     email: EmailStr                # Mismo campo
> ```
>
> **Con Base (DRY - Don't Repeat Yourself):**
>
> ```python
> class UsuarioBase(BaseModel):
>     nombre: str = Field(..., max_length=100)
>     email: EmailStr
>
> class UsuarioCreate(UsuarioBase):
>     password: str  # Solo para crear
>
> class UsuarioUpdate(BaseModel):
>     nombre: str | None = Field(None, max_length=100)
>     email: EmailStr | None = None
>
> class UsuarioResponse(UsuarioBase):
>     id_usuario: int
>     created_at: datetime
> ```
>
> **¿Cuándo usar Base y cuándo no?**
>
> | Situación | Usar |
> |-----------|------|
> | Campos idénticos en múltiples schemas | Base con herencia |
> | Campos diferentes en cada schema | Schemas independientes |
> | Solo 1-2 campos compartidos | Schemas independientes |
> | Más de 3 campos compartidos | Base con herencia |

> **¿Por qué `GeneroEnum(str, Enum)`?**
>
> ```python
> # ❌ Sin Enum - cualquier string es válido
> class UsuarioCreate(BaseModel):
>     genero: str  # "masculino", "femnino", "xxx", "cualquier cosa"
>
> # ✅ Con Enum - solo valores permitidos
> class GeneroEnum(str, Enum):
>     masculino = "masculino"
>     femenino = "femenino"
>     otro = "otro"
>
> class UsuarioCreate(BaseModel):
>     genero: GeneroEnum  # Solo acepta los 3 valores
> ```
>
> **Validación automática:**
>
> ```python
> # Request con valor inválido
> {"genero": "invalido"}
>
> # Respuesta automática de Pydantic
> {
>     "detail": [{
>         "loc": ["body", "genero"],
>         "msg": "value is not a valid enumeration member",
>         "type": "type_error.enum"
>     }]
> }
> ```

### Schema para Crear

```python
class UsuarioCreate(UsuarioBase):
    """Datos para crear un usuario (POST /usuarios/)."""
    password: str = Field(
        ...,
        min_length=6,
        description="Contraseña del usuario"
    )

    @field_validator("password")
    def validar_longitud_maxima(cls, v: str) -> str:
        """bcrypt solo permite contraseñas de ≤72 bytes."""
        max_bytes = 72
        if len(v.encode("utf-8")) > max_bytes:
            raise ValueError(f"La contraseña no puede superar los {max_bytes} bytes")
        return v
```

> **¿Por qué validar longitud máxima de contraseña?**
>
> **El límite de bcrypt:**
>
> bcrypt solo usa los primeros 72 bytes de una contraseña. Si envías más:
>
> ```python
> # Contraseña larga
> password = "a" * 100
>
> # bcrypt ignora los caracteres después del byte 72
> hash1 = bcrypt.hash(password)  # Solo usa primeros 72 bytes
> hash2 = bcrypt.hash(password + "extra")  # ¡Mismo hash!
> ```
>
> **Problema de seguridad:**
>
> Si no validas, un usuario podría crear una contraseña de 100 caracteres pensando que es más segura, pero bcrypt la truncaría.
>
> **Por eso es mejor:**
> 1. Validar y rechazar contraseñas > 72 bytes
> 2. O hashear antes con SHA256 para contraseñas más largas

> **¿Qué es `@field_validator`?**
>
> Un decorador de Pydantic que permite validar campos personalizados:
>
> ```python
> @field_validator("campo_a_validar")
> def nombre_validador(cls, v: tipo) -> tipo:
>     # v es el valor recibido
>     if condicion_invalida(v):
>         raise ValueError("mensaje de error")
>     return v  # Devolver valor (posiblemente modificado)
> ```
>
> **Ejecución:**
>
> 1. Pydantic recibe el JSON
> 2. Convierte tipos básicos (str, int, etc.)
> 3. Ejecuta validadores de campo
> 4. Si todos pasan, crea el objeto

### Schema para Actualizar

```python
class UsuarioUpdate(BaseModel):
    """Datos para actualizar (todos opcionales)."""
    nombre: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    contraseña: str | None = Field(None, min_length=6)
    genero: GeneroEnum | None = None
    telefono: str | None = Field(None, max_length=20)
    fecha_nacimiento: date | None = None

    @field_validator("telefono")
    def validar_telefono(cls, v: str | None) -> str | None:
        if v is None:
            return v
        telefono_limpio = re.sub(r"[\s\-]", "", v)
        patron = r"^(\+\d{1,3})?\d{6,14}$"
        if not re.match(patron, telefono_limpio):
            raise ValueError("Formato de teléfono inválido")
        return telefono_limpio
```

> **¿Por qué todos los campos son opcionales en Update?**
>
> **El problema de PATCH:**
>
> PATCH actualiza parcialmente. Si todos los campos son obligatorios, obligas al cliente a enviar todo:
>
> ```json
> // Solo quiero actualizar el teléfono
> {
>     "telefono": "+34123456789",
>     "nombre": "???",      // ¿Qué pongo?
>     "email": "???",      // ¿Qué pongo?
>     "genero": "???"      // ¿Qué pongo?
> }
> ```
>
> **Con campos opcionales:**
>
> ```json
> // Solo envío lo que quiero cambiar
> {
>     "telefono": "+34123456789"
> }
> ```
>
> **En el servicio:**
>
> ```python
> def actualizar_usuario(db: Session, id: int, datos: UsuarioUpdate):
>     usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
>
>     # Solo actualizar campos proporcionados
>     if datos.nombre is not None:
>         usuario.nombre = datos.nombre
>     if datos.email is not None:
>         usuario.email = datos.email
>     if datos.telefono is not None:
>         usuario.telefono = datos.telefono
>
>     db.commit()
>     return usuario
> ```

> **¿Por qué limpiar el teléfono en el validador?**
>
> ```python
> telefono_limpio = re.sub(r"[\s\-]", "", v)
> ```
>
> Los usuarios pueden introducir teléfonos en diferentes formatos:
>
> ```
> +34 123 456 789
> +34-123-456-789
> 34 123456789
> 123 456 789
> ```
>
> **Sin limpieza:**
>
> ```python
> "+34 123 456 789" == "+34-123-456-789"  # False - diferentes strings
> ```
>
> **Con limpieza:**
>
> ```python
> limpiar("+34 123 456 789")  # "+34123456789"
> limpiar("+34-123-456-789")  # "+34123456789"
> # Ahora son iguales
> ```
>
> **Patrones de teléfono:**
>
> ```python
> patron = r"^(\+\d{1,3})?\d{6,14}$"
> #         └────┬────┘ └──┬──┘
> #           prefijo    números
> #           opcional   6-14 dígitos
> ```
>
> Este patrón acepta:
> - `+34123456789` (con prefijo)
> - `123456789` (sin prefijo)
> - Pero rechaza: `abc`, `123`, `+34`

### Schema de Respuesta

```python
class UsuarioResponse(BaseModel):
    """Datos que devuelve la API (GET /usuarios/)."""
    id_usuario: int
    nombre: str
    email: EmailStr
    genero: GeneroEnum | None = None
    telefono: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Permite leer desde ORM
```

> **¿Qué hace `from_attributes = True`?**
>
> **Sin `from_attributes`:**
>
> ```python
> usuario = db.query(Usuario).first()  # Objeto SQLAlchemy
>
> # Error - Pydantic no sabe leer objetos ORM
> UsuarioResponse.model_validate(usuario)
> # ValidationError: Input should be a valid dictionary
> ```
>
> **Con `from_attributes = True`:**
>
> ```python
> usuario = db.query(Usuario).first()  # Objeto SQLAlchemy
>
> # Pydantic accede a los atributos del objeto
> UsuarioResponse.model_validate(usuario)
> # Equivalente a:
> # UsuarioResponse(
> #     id_usuario=usuario.id_usuario,
> #     nombre=usuario.nombre,
> #     ...
> # )
> ```
>
> **¿Por qué se llama `from_attributes` y no `from_orm`?**
>
> En Pydantic v1 se llamaba `orm_mode`. En v2 se renombró a `from_attributes` porque:
> - Es más descriptivo
> - Funciona con cualquier objeto que tenga atributos, no solo ORMs
> - También funciona con dataclasses, attrs, etc.

## Validadores

### Validador de Campo

```python
from pydantic import field_validator
import re

class UsuarioUpdate(BaseModel):
    telefono: str | None = None

    @field_validator("telefono")
    def validar_telefono(cls, v):
        if v is None:
            return v
        if not re.match(r"^\+?\d{6,15}$", v):
            raise ValueError("Teléfono inválido")
        return v
```

> **¿Cuándo usar `@field_validator` vs `@model_validator`?**
>
> | Tipo | Uso | Ejemplo |
> |------|-----|---------|
> | `@field_validator` | Validar un solo campo | Formato de email, teléfono |
> | `@model_validator` | Validar múltiples campos | Contraseñas coinciden |
>
> **`@field_validator` - Validación de un campo:**
>
> ```python
> @field_validator("telefono")
> def validar_telefono(cls, v):
>     # Solo puedes acceder a v (el valor del campo)
>     if not re.match(r"^\+?\d{6,15}$", v):
>         raise ValueError("Formato inválido")
>     return v
> ```
>
> **`@model_validator` - Validación entre campos:**
>
> ```python
> @model_validator(mode="after")
> def validar_passwords_iguales(self):
>     # Puedes acceder a todos los campos con self
>     if self.password != self.confirmar_password:
>         raise ValueError("Las contraseñas no coinciden")
>     return self
> ```

### Validador de Modelo

```python
from pydantic import model_validator

class UsuarioCreate(BaseModel):
    password: str
    confirmar_password: str

    @model_validator(mode="after")
    def validar_passwords_iguales(self):
        if self.password != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
```

> **¿Por qué `mode="after"`?**
>
> Pydantic v2 tiene tres modos de validación:
>
> | Modo | Cuándo se ejecuta | Acceso |
> |------|-------------------|--------|
> | `mode="before"` | Antes de convertir tipos | Valores raw (dict, etc.) |
> | `mode="after"` | Después de convertir tipos | Objeto con tipos correctos |
>
> **Ejemplo:**
>
> ```python
> class Usuario(BaseModel):
>     edad: int
>     nombre: str
>
>     @model_validator(mode="before")
>     def validar_antes(cls, data):
>         # data es un dict: {"edad": "25", "nombre": "Juan"}
>         # Tipos aún no convertidos
>         return data
>
>     @model_validator(mode="after")
>     def validar_despues(self):
>         # self es un Usuario con tipos convertidos
>         # self.edad es int, self.nombre es str
>         if self.edad < 18:
>             raise ValueError("Debe ser mayor de edad")
>         return self
> ```
>
> **Usar `mode="after"` cuando:**
> - Necesitas acceder a valores ya convertidos
> - Comparas campos entre sí
> - Quieres usar los métodos del modelo

## Tipos de Datos

### Tipos Básicos

```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List

class Ejemplo(BaseModel):
    # Obligatorios
    nombre: str
    edad: int = Field(..., ge=0, le=150)  # Mayor o igual a 0, menor o igual a 150
    precio: float = Field(..., gt=0)       # Mayor que 0
    activo: bool = True                    # Con valor por defecto

    # Opcionales
    descripcion: str | None = None

    # Fechas
    fecha_nacimiento: date | None = None
    creado_en: datetime

    # Listas
    tags: List[str] = []

    # Con restricciones
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
```

> **¿Qué significan las restricciones de Field?**
>
> | Restricción | Significado | Ejemplo |
> |-------------|-------------|---------|
> | `...` | Obligatorio (sin valor por defecto) | `Field(...)` |
> | `ge=n` | Mayor o igual que n | `ge=0` → ≥ 0 |
> | `gt=n` | Mayor que n | `gt=0` → > 0 |
> | `le=n` | Menor o igual que n | `le=150` → ≤ 150 |
> | `lt=n` | Menor que n | `lt=100` → < 100 |
> | `min_length=n` | Longitud mínima | `min_length=3` |
> | `max_length=n` | Longitud máxima | `max_length=100` |
> | `pattern=r"..."` | Regex | `pattern=r"^\d+$"` |
>
> **Ejemplos prácticos:**
>
> ```python
> # Edad: entero positivo, máximo 150
> edad: int = Field(..., ge=0, le=150)
>
> # Precio: positivo, puede ser decimal
> precio: float = Field(..., gt=0)
>
> # Nombre: entre 2 y 100 caracteres
> nombre: str = Field(..., min_length=2, max_length=100)
>
> # Email con regex
> email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
> ```

### Tipos Especiales

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from uuid import UUID

class Ejemplo(BaseModel):
    email: EmailStr           # Valida formato de email
    web: HttpUrl              # Valida URL
    id: UUID                  # UUID
```

> **¿Por qué usar tipos especiales de Pydantic?**
>
> **`EmailStr` vs `str` con regex:**
>
> ```python
> # Con regex - solo valida formato básico
> email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
>
> # Con EmailStr - validación completa
> email: EmailStr
> ```
>
> **`EmailStr` valida más que formato:**
> - Formato correcto
> - Dominio existe (si `email-validator` está instalado)
> - Normalización (convierte a minúsculas)
>
> **`HttpUrl` valida:**
> - Protocolo (http/https)
> - Formato de URL
> - Puede extraer componentes: `url.scheme`, `url.host`, `url.path`

## Field

```python
from pydantic import BaseModel, Field

class Producto(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre del producto",
        examples=["Camiseta", "Pantalón"]
    )

    precio: float = Field(
        ...,
        gt=0,
        description="Precio en euros",
        examples=[19.99, 29.99]
    )

    stock: int = Field(
        default=0,
        ge=0,
        description="Cantidad disponible"
    )
```

> **¿Por qué usar Field en lugar de anotaciones directas?**
>
> **Sin Field:**
>
> ```python
> class Producto(BaseModel):
>     nombre: str  # ¿Longitud máxima? ¿Ejemplos? ¿Descripción?
>     precio: float  # ¿Puede ser negativo?
>     stock: int = 0  # ¿Mínimo?
> ```
>
> **Con Field:**
>
> ```python
> class Producto(BaseModel):
>     nombre: str = Field(..., max_length=100)
>     precio: float = Field(..., gt=0)
>     stock: int = Field(0, ge=0)
> ```
>
> **Beneficios de Field:**
>
> 1. **Validación**: Restricciones numéricas y de longitud
> 2. **Documentación**: `description` y `examples` aparecen en Swagger
> 3. **Metadata**: Información adicional para herramientas
>
> **`examples` vs `example` (Pydantic v2):**
>
> ```python
> # Pydantic v1
> class Config:
>     schema_extra = {"example": {"nombre": "Test"}}
>
> # Pydantic v2
> nombre: str = Field(..., examples=["Test1", "Test2"])
> ```

## Configuración

```python
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: str

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id_usuario": 1,
                "nombre": "Juan García",
                "email": "juan@email.com"
            }
        }
```

> **Opciones importantes de Config:**
>
> | Opción | Propósito |
> |--------|-----------|
> | `from_attributes = True` | Permite leer desde objetos ORM |
> | `json_schema_extra` | Ejemplos para Swagger |
> | `str_strip_whitespace = True` | Elimina espacios al inicio/final |
> | `str_to_lower = True` | Convierte strings a minúsculas |
> | `validate_assignment = True` | Valida al modificar atributos |
>
> **Ejemplo completo:**
>
> ```python
> class UsuarioResponse(BaseModel):
>     nombre: str
>     email: str
>
>     class Config:
>         from_attributes = True
>         str_strip_whitespace = True
>         str_to_lower = False  # No convertir email a minúsculas
>         validate_assignment = True
>         json_schema_extra = {
>             "example": {
>                 "nombre": "Juan García",
>                 "email": "juan@email.com"
>             }
>         }
> ```

## Relaciones en Schemas

```python
from typing import List

class EquipoResponse(BaseModel):
    id_equipo: int
    nombre: str

    class Config:
        from_attributes = True

class LigaResponse(BaseModel):
    id_liga: int
    nombre: str
    equipos: List[EquipoResponse] = []

    class Config:
        from_attributes = True
```

> **¿Cómo manejar relaciones circulares?**
>
> **Problema:**
>
> ```python
> class EquipoResponse(BaseModel):
>     liga: LigaResponse  # LigaResponse no existe todavía
>
> class LigaResponse(BaseModel):
>     equipos: List[EquipoResponse]  # EquipoResponse no existe todavía
> ```
>
> **Solución 1: `model_rebuild`**
>
> ```python
> class EquipoResponse(BaseModel):
>     liga: "LigaResponse"  # String, no clase
>
> class LigaResponse(BaseModel):
>     equipos: List[EquipoResponse]
>
> EquipoResponse.model_rebuild()  # Resolver referencias
> ```
>
> **Solución 2: `from __future__ import annotations` (Python 3.7+)**
>
> ```python
> from __future__ import annotations
>
> class EquipoResponse(BaseModel):
>     liga: LigaResponse  # Ya funciona como string automáticamente
> ```
>
> **Solución 3: Omitir la relación en un lado**
>
> ```python
> # Equipo conoce su liga
> class EquipoResponse(BaseModel):
>     nombre: str
>     liga: LigaResponse
>
> # Liga no muestra equipos (para evitar anidamiento infinito)
> class LigaResponse(BaseModel):
>     nombre: str
>     # Sin equipos
> ```

## Uso en Routers

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.api.services.usuario_service import crear_usuario

router = APIRouter(prefix="/usuarios")

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario."""
    usuario = crear_usuario(db, datos)
    return usuario

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obtener(id_usuario: int, db: Session = Depends(get_db)):
    """Obtener usuario por ID."""
    usuario = obtener_usuario_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{id_usuario}", response_model=UsuarioResponse)
def actualizar(id_usuario: int, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    """Actualizar usuario."""
    usuario = actualizar_usuario(db, id_usuario, datos)
    return usuario
```

### response_model

El parámetro `response_model`:
1. Valida la respuesta contra el schema
2. Filtra campos que no están en el schema
3. Convierte tipos automáticamente
4. Genera documentación OpenAPI

> **¿Qué hace exactamente `response_model`?**
>
> ```python
> # Sin response_model
> @router.get("/usuarios/{id}")
> def obtener(id: int, db: Session = Depends(get_db)):
>     usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
>     return usuario
> # Devuelve: {id_usuario, nombre, email, contraseña_hash, created_at, ...}
> #           ¡contraseña_hash está expuesto!
>
> # Con response_model
> @router.get("/usuarios/{id}", response_model=UsuarioResponse)
> def obtener(id: int, db: Session = Depends(get_db)):
>     usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
>     return usuario
> # Devuelve: {id_usuario, nombre, email, created_at}
> #           Solo campos de UsuarioResponse
> ```
>
> **Proceso interno:**
>
> 1. Router devuelve objeto SQLAlchemy (`Usuario`)
> 2. FastAPI lo pasa a `UsuarioResponse.model_validate()`
> 3. Pydantic:
>    - Lee atributos del objeto (gracias a `from_attributes=True`)
>    - Filtra campos no definidos en el schema
>    - Convierte tipos si es necesario
>    - Valida valores
> 4. Resultado se serializa a JSON

## Errores de Validación Automáticos

```json
// Petición con datos inválidos
{
    "nombre": "Ju",
    "email": "no-es-email",
    "password": "123"
}

// Respuesta de error (422)
{
    "detail": [
        {
            "loc": ["body", "nombre"],
            "msg": "String should have at least 3 characters",
            "type": "string_too_short"
        },
        {
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email"
        },
        {
            "loc": ["body", "password"],
            "msg": "String should have at least 6 characters",
            "type": "string_too_short"
        }
    ]
}
```

> **¿Cómo personalizar los mensajes de error?**
>
> **Mensajes por defecto (inglés):**
>
> ```python
> nombre: str = Field(..., min_length=3)
> # Error: "String should have at least 3 characters"
> ```
>
> **Personalizados:**
>
> ```python
> from pydantic import field_validator

>
> class UsuarioCreate(BaseModel):
>     nombre: str = Field(..., min_length=3)
>
>     @field_validator("nombre")
>     @classmethod
>     def validar_nombre(cls, v: str) -> str:
>         if len(v) < 3:
>             raise ValueError("El nombre debe tener al menos 3 caracteres")
>         return v
> ```
>
> **Resultado:**
>
> ```json
> {
>     "detail": [{
>         "loc": ["body", "nombre"],
>         "msg": "El nombre debe tener al menos 3 caracteres",
>         "type": "value_error"
>     }]
> }
> ```
>
> **Captura global de errores:**
>
> ```python
> from fastapi import FastAPI
> from fastapi.exceptions import RequestValidationError
>
> app = FastAPI()
>
> @app.exception_handler(RequestValidationError)
> async def validation_exception_handler(request, exc):
>     errores = []
>     for error in exc.errors():
>         errores.append({
>             "campo": ".".join(str(x) for x in error["loc"]),
>             "mensaje": error["msg"]
>         })
>     return {"errores": errores}
> ```