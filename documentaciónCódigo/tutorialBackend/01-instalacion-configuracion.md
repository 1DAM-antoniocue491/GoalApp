# Instalación y Configuración

## Requisitos

- Python 3.11 o superior
- MySQL 8.0 o superior (opcional para desarrollo)
- Git

## Instalación

### Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/goalapp.git
cd goalapp/backend
```

### Crear entorno virtual

```bash
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Linux/Mac:
source .venv/bin/activate
```

**¿Por qué usar un entorno virtual?**

Los entornos virtuales son **fundamentales** en Python por varias razones:

1. **Aislamiento de dependencias**: Cada proyecto puede tener versiones diferentes de las mismas librerías sin conflictos. Por ejemplo, un proyecto podría necesitar `fastapi==0.100.0` mientras otro necesita `fastapi==0.110.0`.

2. **Reproducibilidad**: Garantiza que todos los desarrolladores trabajen con las mismas versiones exactas de las dependencias.

3. **Limpieza del sistema**: No "contamina" la instalación global de Python con paquetes específicos del proyecto.

4. **Facilidad de despliegue**: El archivo `requirements.txt` generado desde un entorno virtual contiene exactamente lo necesario para producción.

**¿Qué pasa si no uso entorno virtual?** Los paquetes se instalarían en el Python global, causando conflictos entre proyectos y haciendo difícil saber qué dependencias pertenecen a qué proyecto.

### Instalar dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```
fastapi
uvicorn[standard]
sqlalchemy
pymysql
alembic
python-dotenv
pydantic[email]
pydantic-settings
python-jose
passlib[bcrypt]
python-multipart
cryptography
```

**¿Por qué estas dependencias específicas?**

| Dependencia | Propósito |
|------------|-----------|
| `fastapi` | Framework web. Alto rendimiento, validación automática con Pydantic, documentación OpenAPI generada. |
| `uvicorn[standard]` | Servidor ASGI. `[standard]` instala `uvloop` y `httptools` que mejoran el rendimiento hasta 3x. |
| `sqlalchemy` | ORM. Escribe consultas en Python, previene inyecciones SQL, permite cambiar de BD sin modificar código. |
| `pymysql` | Driver MySQL. Necesario porque SQLAlchemy no incluye drivers por defecto. |
| `alembic` | Migraciones. Versiona cambios en BD igual que código en Git. |
| `python-dotenv` | Carga variables de `.env`. Separa configuración sensible del código. |
| `pydantic[email]` | Validación. `[email]` instala `email-validator` para validar emails (formato, dominio existe). |
| `pydantic-settings` | Configuración. Carga desde variables de entorno y `.env`. |
| `python-jose` | JWT. Necesaria para autenticación stateless. |
| `passlib[bcrypt]` | Hash contraseñas. Bcrypt es deliberadamente lento para resistir ataques de fuerza bruta. |
| `python-multipart` | Formularios. Necesario para `OAuth2PasswordRequestForm` en login. |
| `cryptography` | Criptografía. Dependencia de `python-jose` para firmar tokens JWT. |

## Configuración

### Variables de entorno

Crear archivo `.env` en `backend/.env`:

```env
# Base de datos
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/futbol_app
DATABASE_ECHO=True

# Seguridad JWT
SECRET_KEY=tu_clave_secreta_aqui_cambiar
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Aplicación
APP_NAME=Liga Amateur App
API_VERSION=v1
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logs
LOG_LEVEL=INFO

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=
FRONTEND_URL=http://localhost:5173
RESET_TOKEN_EXPIRE_MINUTES=30
```

**¿Por qué usar variables de entorno?**

Las variables de entorno son una práctica fundamental en desarrollo moderno:

1. **Seguridad**: Las credenciales, claves API y secretos **nunca** deben estar en el código fuente. Si se suben a Git, quedan expuestos en el historial para siempre.

2. **Configuración por entorno**: El mismo código funciona en desarrollo, staging y producción solo cambiando las variables de entorno. No necesitas modificar el código para desplegar.

3. **12-Factor App**: Es una de las prácticas recomendadas: "Store config in the environment".

4. **Docker y despliegue**: Los contenedores inyectan configuración mediante variables de entorno. Es el estándar en Kubernetes, Docker Compose, etc.

**¿Por qué `.env` y no variables de entorno del sistema?**

El archivo `.env` es conveniente para desarrollo local:
- Se puede versionar un `.env.example` como plantilla
- Los desarrolladores no necesitan configurar variables en su sistema
- Es más fácil de gestionar que variables de entorno del sistema operativo
- Herramientas como `python-dotenv` lo cargan automáticamente

Generar clave secreta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**¿Por qué generar una clave secreta con `secrets`?**

1. **Entropía suficiente**: `secrets.token_urlsafe(64)` genera 64 bytes de aleatoriedad criptográficamente segura, suficiente para JWT.

2. **`secrets` vs `random`**: El módulo `secrets` usa fuentes de entropía del sistema operativo (como `/dev/urandom` en Linux), mientras que `random` es predecible y NO debe usarse para seguridad.

3. **Longitud recomendada**: Para HS256, la clave debe tener al menos 256 bits (32 bytes). Usamos 64 bytes (512 bits) para mayor seguridad.

**Error común**: Usar claves simples como "mi_clave_secreta" o "password123". Estas son vulnerables a ataques de fuerza bruta porque tienen poca entropía.

### Configuración de la aplicación

El archivo `app/config.py` lee las variables de entorno:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str
    DATABASE_ECHO: bool

    # Seguridad JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Aplicación
    APP_NAME: str
    API_VERSION: str
    ENVIRONMENT: str
    PORT: int
    HOST: str

    # CORS
    CORS_ORIGINS: str

    # Logs
    LOG_LEVEL: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }
```

**¿Por qué usar `pydantic_settings` en lugar de `os.environ`?**

```python
# ❌ Forma manual (problemática)
import os
DATABASE_URL = os.environ.get("DATABASE_URL")  # str | None
PORT = int(os.environ.get("PORT", "8000"))     # Hay que convertir tipos

# ✅ Con pydantic_settings (recomendado)
class Settings(BaseSettings):
    DATABASE_URL: str           # Ya es str, no None
    PORT: int = 8000            # Conversión automática
```

**Ventajas:**

1. **Validación automática**: Si `PORT` no es un número válido, Pydantic lanza un error claro antes de iniciar la aplicación.

2. **Tipado fuerte**: Los IDEs pueden autocompletar y verificar tipos. Con `os.environ` solo obtienes strings.

3. **Valores por defecto**: Se pueden definir defaults fácilmente (`PORT: int = 8000`).

4. **Recarga en caliente**: En desarrollo, si cambias `.env`, se puede recargar sin reiniciar.

5. **Documentación automática**: Las variables están documentadas como atributos de clase con tipos.

## Base de datos

### Opción A: MySQL (producción)

```sql
CREATE DATABASE futbol_app
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER 'goalapp'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON futbol_app.* TO 'goalapp'@'localhost';
FLUSH PRIVILEGES;
```

**¿Por qué UTF8MB4 y no UTF8?**

**¡Este es un error muy común!** En MySQL, `utf8` **NO** es UTF-8 real.

- `utf8` en MySQL es "utf8mb3", un subconjunto de UTF-8 que solo soporta hasta 3 bytes por carácter.
- `utf8mb4` es UTF-8 completo, soporta hasta 4 bytes.

**Consecuencias de usar `utf8`:**
- No puedes guardar emojis 🎉👤⚽ (falla silenciosamente o da error)
- Algunos caracteres asiáticos no se guardan correctamente
- Vulnerabilidad de seguridad: se pueden truncar datos maliciosos

**La regla es simple: En MySQL, siempre usa `utf8mb4`, nunca `utf8`.**

**¿Por qué crear un usuario específico para la aplicación?**

```sql
# ❌ Usar root
DATABASE_URL=mysql+pymysql://root:password@localhost/futbol_app

# ✅ Usar usuario con permisos mínimos
DATABASE_URL=mysql+pymysql://goalapp:password@localhost/futbol_app
```

**Razones de seguridad:**

1. **Principio de mínimo privilegio**: La aplicación solo necesita permisos sobre su base de datos, no sobre todo el servidor.

2. **Limitar daño**: Si la aplicación es comprometida, el atacante solo puede acceder a `futbol_app`, no a otras bases de datos.

3. **Auditoría**: Cada usuario tiene sus logs de acceso. Puedes saber qué hizo la aplicación vs un administrador.

4. **Prevención de errores**: El usuario `goalapp` no puede accidentalmente ejecutar `DROP DATABASE mysql` o modificar permisos.

```bash
mysql -u goalapp -p futbol_app < app/database/init.sql
```

### Conexión a la base de datos

`app/database/connection.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..config import settings

if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**¿Por qué configuración diferente para SQLite vs MySQL?**

**SQLite** está diseñado para ser embebido en aplicaciones de un solo proceso:
- `check_same_thread=False`: SQLite por defecto solo permite acceso desde el thread que creó la conexión. FastAPI es asíncrono y puede usar múltiples threads, por eso necesitamos desactivar esta restricción.
- No tiene pool de conexiones porque SQLite usa un solo archivo.

**MySQL** requiere un pool de conexiones para rendimiento:

| Parámetro | Valor | ¿Por qué? |
|-----------|-------|-----------|
| `pool_pre_ping=True` | Habilitado | Verifica que la conexión está viva antes de usarla. MySQL cierra conexiones inactivas por timeout, y sin esto obtendrías errores intermitentes. |
| `pool_recycle=3600` | 1 hora | Recicla conexiones después de 1 hora. MySQL tiene `wait_timeout` (default 8h), pero es mejor reciclar antes para evitar conexiones obsoletas. |
| `pool_size=10` | 10 conexiones | Número de conexiones permanentes. 10 es bueno para aplicaciones típicas. Ajusta según carga. |
| `max_overflow=20` | 20 extra | Conexiones adicionales cuando el pool está lleno. Total máximo = 10 + 20 = 30 conexiones. |

**¿Qué pasa si no configuro el pool?**

```python
# Sin pool - crea nueva conexión cada petición
engine = create_engine(DATABASE_URL)
# Problema: Conectar a MySQL toma ~50ms. Con 100 peticiones/segundo = 5 segundos perdidos.

# Con pool - reutiliza conexiones
# La conexión ya está establecida, solo toma ~1ms del pool
```

**¿Por qué `autocommit=False`?**

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- `autocommit=False`: Cada cambio requiere `db.commit()` explícito. Esto permite transacciones atómicas y rollback en errores.
- `autoflush=False`: No envía cambios automáticamente a la BD antes de consultas. Mejor control de cuándo se ejecutan las queries.

## Ejecución

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**¿Por qué estos parámetros?**

| Parámetro | ¿Por qué? |
|-----------|-----------|
| `--host 0.0.0.0` | Escucha en todas las interfaces de red. Necesario para acceder desde otros dispositivos en la red. `127.0.0.1` solo permite acceso local. |
| `--port 8000` | Puerto estándar para desarrollo. Los puertos < 1024 requieren root en Linux. |
| `--reload` | Recarga automáticamente cuando detecta cambios en archivos. **Solo para desarrollo**, en producción usa Gunicorn sin reload. |

**¿Por qué Uvicorn y no Gunicorn directamente?**

- **Uvicorn** es un servidor ASGI, diseñado para aplicaciones asíncronas como FastAPI.
- **Gunicorn** es un servidor WSGI para aplicaciones síncronas como Flask/Django.

En desarrollo: `uvicorn` es suficiente.

En producción: `gunicorn --worker-class uvicorn.workers.UvicornWorker app.main:app`

Gunicorn actúa como gestor de procesos y Uvicorn como worker ASGI.

### Verificar ejecución

- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

**¿Por qué FastAPI genera documentación automáticamente?**

FastAPI usa los **type hints** y **Pydantic models** para generar especificación OpenAPI (Swagger).

```python
@router.post("/usuarios/", response_model=UsuarioResponse)
def crear(datos: UsuarioCreate):
    ...
```

De esto, FastAPI genera:
- Schema de entrada (`UsuarioCreate`)
- Schema de salida (`UsuarioResponse`)
- Ejemplos automáticos
- Validación documentada

**Ventaja**: La documentación nunca está desactualizada porque se genera del código mismo.

**Swagger vs ReDoc:**
- **Swagger UI** (`/docs`): Interactivo, puedes probar endpoints directamente.
- **ReDoc** (`/redoc`): Más limpio visualmente, mejor para leer la documentación.

Respuesta esperada en `/`:

```json
{
  "mensaje": "Bienvenido a Liga Amateur App",
  "version": "v1",
  "entorno": "development",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

## Solución de problemas

### Error: "Module not found"

```bash
# Verificar entorno virtual activado
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac

# Reinstalar dependencias
pip install -r requirements.txt
```

**¿Por qué ocurre este error?**

1. **Entorno virtual no activado**: `pip install` instala en el Python global, pero el código busca en el entorno virtual.

2. **Terminal diferente**: Si usas PowerShell, Git Bash y CMD, cada uno tiene su contexto. Asegúrate de activar el entorno en cada uno.

3. **IDE configurado incorrectamente**: VSCode/PyCharm pueden usar un intérprete diferente. Verifica que use `./.venv/bin/python`.

### Error: "Can't connect to MySQL server"

```bash
# Verificar que MySQL está corriendo
# Windows: Services → MySQL80
# Linux: sudo systemctl status mysql

# Verificar credenciales en .env
```

**Causas comunes:**

1. **MySQL no iniciado**: El servicio no está corriendo.
2. **Puerto incorrecto**: MySQL por defecto usa 3306, pero puede estar en otro puerto.
3. **Firewall**: Bloquea conexiones al puerto 3306.
4. **Usuario sin permisos**: El usuario no tiene permiso para conectarse desde tu IP (`'goalapp'@'localhost'` vs `'goalapp'@'%'` para cualquier IP).

### Error: "CORS blocked"

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:19006
```

**¿Qué es CORS y por qué bloquea las peticiones?**

**CORS** (Cross-Origin Resource Sharing) es una política de seguridad del navegador.

**Problema**: El frontend corre en `localhost:5173` y el backend en `localhost:8000`. Para el navegador, son "orígenes diferentes".

```
Frontend: http://localhost:5173  →  Backend: http://localhost:8000
          origen diferente          origen diferente
```

El navegador bloquea peticiones entre orígenes diferentes **por seguridad**:
- Previene que un sitio malicioso robe datos de tu sesión en otro sitio
- Previene CSRF (Cross-Site Request Forgery)

**Solución**: El backend debe declarar explícitamente qué orígenes permite:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Solo este origen puede acceder
    ...
)
```

**¡En producción NUNCA uses `["*"]`!**

```python
# ❌ MUY INSEGURO - permite cualquier origen
allow_origins=["*"]

# ✅ SEGURO - solo dominios específicos
allow_origins=["https://midominio.com", "https://www.midominio.com"]
```

Usar `["*"]` en producción permite que cualquier sitio web haga peticiones a tu API, exponiendo datos de usuarios autenticados.