# INFORME DE CORRECCIÓN DE ERRORES EN EL BACKEND

## Resumen

Se identificaron y corrigieron múltiples errores que impedían el funcionamiento correcto del endpoint de creación de usuarios (`POST /api/v1/usuarios/`).

---

## Errores Encontrados y Soluciones

### 1. Error en Pydantic v2 field_validator

**Archivo:** `backend/app/schemas/usuario.py`

**Problema:**
El decorador `@field_validator("contraseña")` usaba el alias del campo en lugar del nombre real del campo. En Pydantic v2, los field_validators deben usar el nombre real del campo, no el alias.

```python
# Código incorrecto
@field_validator("contraseña")  # "contraseña" es un alias, no el nombre del campo
def validar_longitud_maxima(cls, v: str) -> str:
```

**Solución:**
Cambiar el decorador para usar el nombre real del campo:

```python
# Código correcto
@field_validator("password")  # "password" es el nombre real del campo
def validar_longitud_maxima(cls, v: str) -> str:
```

---

### 2. Error de acceso a campo con alias en el servicio

**Archivo:** `backend/app/api/services/usuario_service.py`

**Problema:**
El servicio accedía al campo usando el alias `datos.contraseña` en lugar del nombre real del campo. En Pydantic v2, el acceso por atributo usa el nombre real del campo.

```python
# Código incorrecto
usuario = Usuario(
    nombre=datos.nombre,
    email=datos.email,
    contraseña_hash=hash_password(datos.contraseña)  # Error: el campo es 'password'
)
```

**Solución:**
Cambiar el acceso al campo usando el nombre real:

```python
# Código correcto
usuario = Usuario(
    nombre=datos.nombre,
    email=datos.email,
    contraseña_hash=hash_password(datos.password)  # Usar el nombre real del campo
)
```

También se actualizó la función `actualizar_usuario` para manejar ambos casos (`UsuarioCreate` usa `password` con alias, mientras que `UsuarioUpdate` usa `contraseña` directamente).

---

### 3. Error de parseo de URL de base de datos

**Archivo:** `backend/app/main.py`

**Problema:**
El código asumía que la URL de base de datos siempre tendría el formato MySQL/PostgreSQL con credenciales (`user:pass@host/db`), causando un `IndexError` con SQLite:

```python
# Código incorrecto
print(f"[INFO] Conectando a base de datos: {settings.DATABASE_URL.split('@')[1]}")
# IndexError: list index out of range para URLs como 'sqlite:///./db.db'
```

**Solución:**
Añadir lógica para manejar ambos formatos de URL:

```python
# Código correcto
db_url = settings.DATABASE_URL
if '@' in db_url:
    # MySQL/PostgreSQL con credenciales: mostrar solo host/db
    print(f"[INFO] Conectando a base de datos: {db_url.split('@')[1]}")
else:
    # SQLite: mostrar toda la URL (no tiene credenciales)
    print(f"[INFO] Conectando a base de datos: {db_url}")
```

---

### 4. Soporte para SQLite en connection.py

**Archivo:** `backend/app/database/connection.py`

**Problema:**
La configuración del engine usaba opciones de pool que no son soportadas por SQLite (`pool_pre_ping`, `pool_recycle`, `pool_size`, `max_overflow`).

**Solución:**
Añadir lógica condicional para configurar el engine según el tipo de base de datos:

```python
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite no soporta pool_pre_ping ni pool_recycle
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}  # Necesario para SQLite en FastAPI
    )
else:
    # MySQL
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20
    )
```

---

### 5. Incompatibilidad entre passlib y bcrypt 5.x

**Archivo:** `backend/requirements.txt` (implícito)

**Problema:**
La versión de `passlib` instalada (1.7.4) no es compatible con `bcrypt` 5.x. Se producía un error al intentar hashear contraseñas:
```
(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Solución:**
Downgrade de bcrypt a versión 4.x:
```bash
pip install "bcrypt>=4.0.0,<5.0.0"
```

**Recomendación:**
Actualizar el archivo `requirements.txt` para especificar la restricción de versión:
```
bcrypt>=4.0.0,<5.0.0
```

---

## Archivos Modificados

1. `backend/app/schemas/usuario.py` - Línea 40: Cambio en field_validator
2. `backend/app/api/services/usuario_service.py` - Líneas 101, 170-173: Corrección de acceso a campos
3. `backend/app/main.py` - Líneas 39-44: Manejo de URLs de base de datos
4. `backend/app/database/connection.py` - Líneas 10-22: Soporte para SQLite
5. Dependencias: bcrypt downgraded de 5.0.0 a 4.3.0

---

## Prueba Exitosa

Después de realizar las correcciones, se ejecutó una petición de prueba:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Antonio", "email": "antonio@gmail.com", "password": "123456789"}'
```

**Respuesta exitosa:**
```json
{
  "id_usuario": 1,
  "nombre": "Antonio",
  "email": "antonio@gmail.com",
  "created_at": "2026-03-11T18:34:49",
  "updated_at": "2026-03-11T18:34:49"
}
```

---

## Recomendaciones Adicionales

1. **Actualizar requirements.txt** para fijar la versión de bcrypt:
   ```
   bcrypt>=4.0.0,<5.0.0
   ```

2. **Considerar usar el mismo nombre de campo** en todos los schemas para evitar confusión. Actualmente:
   - `UsuarioCreate` usa `password` con alias `contraseña`
   - `UsuarioUpdate` usa `contraseña` directamente

   Se recomienda unificar para usar consistentemente un solo nombre de campo.

3. **Revisar la configuración de la base de datos MySQL** ya que no estaba accesible durante las pruebas. Se usó SQLite temporalmente para verificar el funcionamiento del endpoint.