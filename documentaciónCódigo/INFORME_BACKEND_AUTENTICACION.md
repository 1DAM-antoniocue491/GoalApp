# INFORME DE DESARROLLO Y PRUEBAS DEL BACKEND

**Fecha:** 11/03/2026
**Proyecto:** GoalApp - Gestión de Ligas de Fútbol Amateur

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Errores Encontrados y Correcciones](#errores-encontrados-y-correcciones)
3. [Pruebas Realizadas](#pruebas-realizadas)
4. [Archivos Modificados](#archivos-modificados)
5. [Estado de Dependencias](#estado-de-dependencias)
6. [Recomendaciones](#recomendaciones)

---

## 1. Resumen Ejecutivo

Se ha corregido el sistema de autenticación del backend y se han probado exitosamente todos los endpoints relacionados con:
- Registro de usuarios
- Login y obtención de tokens JWT
- Autorización basada en roles
- Gestión de roles (CRUD)

El sistema está completamente funcional y la base de datos MySQL contiene los datos iniciales necesarios.

---

## 2. Errores Encontrados y Correcciones

### 2.1 Error en Pydantic v2 field_validator

**Archivo:** `backend/app/schemas/usuario.py`
**Línea:** 40

**Problema:**
El decorador `@field_validator("contraseña")` usaba el alias del campo en lugar del nombre real. En Pydantic v2, los field_validators deben usar el nombre real del campo.

```python
# ❌ Código incorrecto
@field_validator("contraseña")  # "contraseña" es un alias
def validar_longitud_maxima(cls, v: str) -> str:

# ✅ Código corregido
@field_validator("password")  # "password" es el nombre real del campo
def validar_longitud_maxima(cls, v: str) -> str:
```

---

### 2.2 Error de acceso a campo con alias en el servicio

**Archivo:** `backend/app/api/services/usuario_service.py`
**Líneas:** 101, 170-173

**Problema:**
El servicio accedía al campo usando el alias `datos.contraseña` cuando el campo real se llama `password`.

```python
# ❌ Código incorrecto
contraseña_hash=hash_password(datos.contraseña)

# ✅ Código corregido
contraseña_hash=hash_password(datos.password)
```

---

### 2.3 Error de parseo de URL de base de datos

**Archivo:** `backend/app/main.py`
**Líneas:** 39-44

**Problema:**
El código asumía que la URL de base de datos siempre tendría el formato MySQL/PostgreSQL con credenciales (`user:pass@host/db`), causando un `IndexError` con URLs de SQLite.

```python
# ❌ Código incorrecto
print(f"[INFO] Conectando a base de datos: {settings.DATABASE_URL.split('@')[1]}")

# ✅ Código corregido
db_url = settings.DATABASE_URL
if '@' in db_url:
    # MySQL/PostgreSQL con credenciales
    print(f"[INFO] Conectando a base de datos: {db_url.split('@')[1]}")
else:
    # SQLite sin credenciales
    print(f"[INFO] Conectando a base de datos: {db_url}")
```

---

### 2.4 Soporte para SQLite en connection.py

**Archivo:** `backend/app/database/connection.py`
**Líneas:** 10-22

**Problema:**
La configuración del engine usaba opciones de pool no soportadas por SQLite.

```python
# ✅ Código corregido (manejo condicional)
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}
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

### 2.5 Incompatibilidad entre passlib y bcrypt 5.x

**Problema:**
La versión de `passlib 1.7.4` no es compatible con `bcrypt 5.x`, causando errores al hashear contraseñas.

```
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Solución:**
Downgrade de bcrypt a versión 4.x:
```bash
pip install "bcrypt>=4.0.0,<5.0.0"
```

---

## 3. Pruebas Realizadas

### 3.1 Registro de Usuario

```bash
POST /api/v1/usuarios/
Content-Type: application/json

{
    "nombre": "Antonio Cuevas Lopez",
    "email": "antonio@gmail.com",
    "password": "123456789"
}
```

**Respuesta:**
```json
{
    "id_usuario": 2,
    "nombre": "Antonio Cuevas Lopez",
    "email": "antonio@gmail.com",
    "created_at": "2026-03-11T18:40:02",
    "updated_at": "2026-03-11T18:40:02"
}
```
**Estado:** ✅ Exitoso

---

### 3.2 Login

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=antonio@gmail.com&password=123456789
```

**Respuesta:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```
**Estado:** ✅ Exitoso

---

### 3.3 Obtener Usuario Actual

```bash
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Respuesta:**
```json
{
    "id_usuario": 2,
    "nombre": "Antonio Cuevas Lopez",
    "email": "antonio@gmail.com",
    "created_at": "2026-03-11T18:40:02",
    "updated_at": "2026-03-11T18:40:02"
}
```
**Estado:** ✅ Exitoso

---

### 3.4 Refresh Token

```bash
POST /api/v1/auth/refresh?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Respuesta:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```
**Estado:** ✅ Exitoso

---

### 3.5 Casos de Error - Autenticación

| Prueba | Respuesta | Estado |
|--------|-----------|--------|
| Login con contraseña incorrecta | `{"detail":"Credenciales incorrectas"}` | ✅ Correcto |
| Login con usuario inexistente | `{"detail":"Credenciales incorrectas"}` | ✅ Correcto |
| Acceso a /me sin token | `{"detail":"Not authenticated"}` | ✅ Correcto |
| Acceso a /me con token inválido | `{"detail":"Token inválido o expirado"}` | ✅ Correcto |

---

### 3.6 Acciones con Rol Admin

Después de asignar el rol `admin` al usuario:

```sql
INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (2, 1);
```

| Endpoint | Acción | Estado |
|----------|--------|--------|
| `GET /api/v1/usuarios/` | Listar todos los usuarios | ✅ Exitoso |
| `POST /api/v1/roles/` | Crear nuevo rol | ✅ Exitoso |
| `DELETE /api/v1/roles/6` | Eliminar rol | ✅ Exitoso |
| `POST /api/v1/roles/asignar/1/2` | Asignar rol a usuario | ✅ Exitoso |

---

## 4. Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `backend/app/schemas/usuario.py` | Corregido field_validator para usar nombre real del campo |
| `backend/app/api/services/usuario_service.py` | Corregido acceso a campo `password` en lugar de alias `contraseña` |
| `backend/app/main.py` | Añadido manejo condicional para URLs de base de datos |
| `backend/app/database/connection.py` | Añadido soporte para SQLite |
| `backend/app/database/init.sql` | Añadidas inserciones de roles iniciales |
| `backend/requirements.txt` | *Recomendado: fijar bcrypt<5.0.0* |

---

## 5. Estado de Dependencias

| Dependencia | Versión Instalada | Versión Recomendada | Estado |
|-------------|-------------------|---------------------|--------|
| FastAPI | ✅ Compatible | - | OK |
| SQLAlchemy | ✅ Compatible | - | OK |
| Pydantic | v2 | - | OK |
| bcrypt | 4.3.0 | >=4.0.0, <5.0.0 | ✅ Corregido |
| passlib | 1.7.4 | - | OK |
| python-jose | ✅ Compatible | - | OK |

---

## 6. Datos Iniciales en Base de Datos

### Roles Disponibles

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | admin | Administrador del sistema con acceso total |
| 2 | coach | Entrenador de equipo |
| 3 | player | Jugador |
| 4 | viewer | Visualizador de información pública |
| 5 | delegate | Delegado de equipo |

### Usuarios Creados

| ID | Nombre | Email | Roles |
|----|--------|-------|-------|
| 1 | Juán García | juan@gmail.com | coach |
| 2 | Antonio Cuevas Lopez | antonio@gmail.com | admin |

---

## 7. Recomendaciones

### 7.1 Actualizar requirements.txt

```txt
bcrypt>=4.0.0,<5.0.0
```

### 7.2 Unificar nombres de campos en schemas

Actualmente existe inconsistencia entre `UsuarioCreate` (campo `password` con alias `contraseña`) y `UsuarioUpdate` (campo `contraseña` directamente). Se recomienda unificar para evitar confusión.

### 7.3 Endpoint público para registro

El endpoint `POST /usuarios/` es público (no requiere autenticación), lo cual es correcto para el registro de usuarios. Mantener así.

### 7.4 Documentar roles y permisos

Se recomienda crear documentación detallada de qué endpoints requieren cada rol:
- `admin`: Acceso total
- `coach`: Gestión de su equipo y alineaciones
- `delegate`: Registrar eventos de partidos
- `player`: Ver su propia información y estadísticas
- `viewer`: Ver información pública

---

## 8. Comandos SQL de Referencia

### Asignar rol a usuario

```sql
-- Asignar rol admin (id=1) a usuario (id=2)
INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (2, 1);

-- Con prevención de duplicados
INSERT IGNORE INTO usuario_rol (id_usuario, id_rol) VALUES (2, 1);
```

### Consultar usuarios con roles

```sql
SELECT u.nombre, u.email, r.nombre as rol
FROM usuarios u
JOIN usuario_rol ur ON u.id_usuario = ur.id_usuario
JOIN roles r ON ur.id_rol = r.id_rol;
```

### Ver todos los roles

```sql
SELECT * FROM roles;
```

---

## 9. Conclusiones

El backend está **completamente funcional** para las siguientes operaciones:

1. ✅ Registro de usuarios
2. ✅ Autenticación (login)
3. ✅ Gestión de tokens JWT
4. ✅ Autorización basada en roles
5. ✅ CRUD de usuarios (con permisos admin)
6. ✅ CRUD de roles (con permisos admin)
7. ✅ Asignación de roles a usuarios (con permisos admin)

**Estado general:** 🟢 Operativo