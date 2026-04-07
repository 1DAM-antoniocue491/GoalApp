# Instalación y Configuración (Para Principiantes)

## Antes de Empezar

### ¿Qué necesitas en tu computadora?

Piensa que vas a cocinar una receta. Necesitas ciertos ingredientes y utensilios antes de empezar:

| Lo que necesitas | ¿Para qué sirve? | Analogía |
|------------------|------------------|----------|
| **Python 3.11+** | El lenguaje de programación | La estufa donde cocinas |
| **MySQL 8.0+** | La base de datos | La nevera gigante |
| **Git** | Para guardar versiones de tu código | Una máquina del tiempo |
| **Editor de código** | Donde escribes el código | Tu cuaderno de recetas |

### ¿Cómo revisar si ya tienes Python?

Abre tu terminal (esa pantalla negra donde escribes comandos) y escribe:

```bash
python --version
```

Si dice algo como `Python 3.11.x` o más alto, ¡estás listo!

Si no, ve a [python.org](https://python.org) y descárgalo.

---

## Paso 1: Descargar el Proyecto

### ¿Qué es "clonar"?

Imagina que alguien construyó una casa y tú quieres una exactamente igual en tu terreno. "Clonar" es como copiar los planos de esa casa para construirla donde tú quieras.

```bash
# Entra a la carpeta donde quieres guardar el proyecto
cd "C:\Users\TuNombre\Desktop"

# Copia el proyecto (como descargar los planos)
git clone https://github.com/tu-usuario/goalapp.git

# Entra a la carpeta del proyecto
cd goalapp/backend
```

---

## Paso 2: Crear un Entorno Virtual

### ¿Qué es un entorno virtual?

Imagina que tienes una **caja de herramientas especial** para este proyecto. Cada proyecto tiene su propia caja con las herramientas que necesita, sin mezclarse con los otros proyectos.

```
Computadora
├── Proyecto A (caja con: Python 3.10, FastAPI 0.100)
├── Proyecto B (caja con: Python 3.11, FastAPI 0.110)
└── Proyecto C (caja con: Python 3.11, Django 4.0)
```

**Cada caja tiene lo que necesita. ¡No se mezclan!**

### ¿Por qué es importante?

Sin un entorno virtual:

```
Tu computadora tendría TODAS las librerías juntas:
📦 fastapi 0.100 (para proyecto A)
📦 fastapi 0.110 (para proyecto B)
📦 django 4.0 (para proyecto C)

¿Cuál usa cada proyecto? ¡Un desastre!
```

Con entorno virtual:

```
Proyecto A:
📦 fastapi 0.100  ← Solo esta versión

Proyecto B:
📦 fastapi 0.110  ← Solo esta versión
```

### Cómo crearlo

```bash
# Crear la caja de herramientas (entorno virtual)
python -m venv .venv

# Abrir la caja (activar el entorno)
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# En Mac/Linux:
source .venv/bin/activate
```

**¿Cómo sé que funcionó?**

Tu terminal cambiará de así:
```
C:\Users\TuNombre\proyecto>
```

A así (verás un `(.venv)` al inicio):
```
(.venv) C:\Users\TuNombre\proyecto>
```

Eso significa que ya estás dentro de tu caja de herramientas.

---

## Paso 3: Instalar las Librerías

### ¿Qué es una librería?

Una **librería** es código que alguien más ya escribió para que tú lo uses. Es como si alguien ya hubiera inventado la rueda y tú solo la compras en lugar de inventarla de nuevo.

### El archivo `requirements.txt`

Este archivo es como una **lista de compras**. Tiene todo lo que necesitas:

```
fastapi           # El constructor principal
uvicorn[standard] # El servidor web
sqlalchemy        # Para hablar con la base de datos
pymysql           # El cable que conecta Python con MySQL
alembic           # Para guardar cambios en la base de datos
python-dotenv     # Para leer configuraciones secretas
pydantic[email]   # Para verificar datos
pydantic-settings # Para configuraciones
python-jose       # Para crear "pases" de seguridad
passlib[bcrypt]   # Para esconder contraseñas
python-multipart  # Para recibir archivos
cryptography      # Para encriptar cosas
```

### Instalar todo

```bash
# Esto lee la lista y descarga todo
pip install -r requirements.txt
```

**¿Qué hace cada librería?**

| Librería | ¿Para qué sirve? | Analogía |
|----------|------------------|----------|
| `fastapi` | Construye la aplicación web | El arquitecto |
| `uvicorn` | Sirve la aplicación (la hace funcionar) | El mesero |
| `sqlalchemy` | Traduce Python a SQL | El traductor |
| `pymysql` | Conecta con MySQL | El cable |
| `alembic` | Guarda versiones de la base de datos | Una máquina del tiempo |
| `python-dotenv` | Lee configuraciones secretas | El cofre con llave |
| `pydantic` | Verifica que los datos sean correctos | El inspector |
| `python-jose` | Crea tokens de seguridad | El guardián |
| `passlib[bcrypt]` | Esconde contraseñas | La caja fuerte |

---

## Paso 4: Configurar las Variables de Entorno

### ¿Qué son las variables de entorno?

Imagina que tienes **secretos** que no quieres que nadie vea:
- La contraseña de tu base de datos
- Una llave secreta para crear tokens
- La dirección de tu base de datos

**No puedes escribir estos secretos en tu código**, porque si alguien lo ve, ¡puede entrar a tu base de datos!

Las **variables de entorno** son como una **hoja de papel escondida** que tu programa lee, pero que no está en el código.

### Crear el archivo `.env`

Crea un archivo llamado `.env` en la carpeta `backend/`:

```env
# ========================================
# BASE DE DATOS (Dónde guardamos la info)
# ========================================

# La dirección de tu base de datos
# Formato: tipo+driver://usuario:contraseña@direccion:puerto/nombre
DATABASE_URL=mysql+pymysql://goalapp:tu_contraseña@localhost:3306/futbol_app

# Mostrar las consultas SQL en pantalla (útil para aprender)
DATABASE_ECHO=True

# ========================================
# SEGURIDAD JWT (Los pases de entrada)
# ========================================

# Una palabra secreta para crear tokens
# ¡Nunca uses esto en producción! Genera una nueva.
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura

# El método para crear tokens
ALGORITHM=HS256

# Cuánto tiempo dura un token (en minutos)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ========================================
# APLICACIÓN (Configuración general)
# ========================================

APP_NAME=Liga Amateur App
API_VERSION=v1
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0

# ========================================
# CORS (Quién puede hablar con tu app)
# ========================================

# Las direcciones de tu frontend (la parte visual)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ========================================
# EMAIL (Para recuperar contraseñas)
# ========================================

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
EMAIL_FROM=tu_email@gmail.com
FRONTEND_URL=http://localhost:5173
RESET_TOKEN_EXPIRE_MINUTES=30
```

### ¿Por qué `.env` y no en el código?

**MALO (❌):**
```python
# código.py - ¡NUNCA HAGAS ESTO!
DATABASE_PASSWORD = "mi_contraseña_secreta_123"
```
- Si subes esto a GitHub, **todos** pueden ver tu contraseña
- Si trabajas en equipo, todos ven la contraseña

**BUENO (✅):**
```python
# código.py
from app.config import settings
password = settings.DATABASE_PASSWORD  # Viene del archivo .env
```
- El archivo `.env` **nunca** se sube a GitHub
- Cada persona tiene su propio `.env` con sus contraseñas
- En producción usas otras contraseñas más seguras

### Generar una clave secreta

La `SECRET_KEY` debe ser muy larga y aleatoria. Nunca uses "password123" o cosas así.

```bash
# Ejecuta esto en tu terminal para generar una clave segura
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Te dará algo como:
```
jX9kL2mN4pQ8rT6vW3yZ5aB7cD9eF1gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0aB
```

¡Copia eso y ponlo en tu `.env`!

---

## Paso 5: Configurar la Base de Datos

### ¿Qué es MySQL?

**MySQL** es como una **nevera gigante** donde guardas toda tu información. Es muy rápida y organizada.

### Crear la base de datos

Abre MySQL (puede ser con MySQL Workbench o la terminal) y ejecuta:

```sql
-- Crear la base de datos (la nevera)
CREATE DATABASE futbol_app
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- Crear un usuario para la aplicación (no uses 'root')
CREATE USER 'goalapp'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';

-- Dar permisos al usuario
GRANT ALL PRIVILEGES ON futbol_app.* TO 'goalapp'@'localhost';

-- Guardar los cambios
FLUSH PRIVILEGES;
```

### ¿Por qué `utf8mb4` y no `utf8`?

**¡Esto es importante!**

En MySQL, `utf8` **NO** es UTF-8 de verdad. Es una versión incompleta que **no puede guardar emojis** 🎉⚽.

```
❌ utf8    → Solo algunos caracteres
✅ utf8mb4 → TODOS los caracteres, incluyendo emojis 🎉
```

**Siempre usa `utf8mb4`** si quieres que tu app pueda guardar emojis y caracteres especiales.

### ¿Por qué crear un usuario separado?

Imagina que tuvieras una **llave maestra** que abre todas las puertas de tu casa.

- Si la pierdes, ¡alguien puede entrar a todas partes!
- Si un ladrón la encuentra, ¡puede robar todo!

**Por eso creamos un usuario específico:**

```
❌ root (usuario administrador) → Puede hacer CUALQUIER cosa
✅ goalapp (usuario de la app)   → Solo puede tocar su propia base de datos
```

Si alguien hackea tu app, solo puede acceder a `futbol_app`, no a todas tus bases de datos.

---

## Paso 6: Configurar la Aplicación

### El archivo `app/config.py`

Este archivo **lee** las variables de tu `.env` y las organiza:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str           # Obligatorio
    DATABASE_ECHO: bool = True  # Por defecto muestra las consultas

    # Seguridad JWT
    SECRET_KEY: str             # Obligatorio
    ALGORITHM: str = "HS256"    # Por defecto
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Por defecto 1 hora

    # Configuración de la app
    APP_NAME: str = "Mi App"    # Por defecto
    API_VERSION: str = "v1"     # Por defecto
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    CORS_ORIGINS: str = ""

    # Logs
    LOG_LEVEL: str = "INFO"

    # Esta línea mágica hace que lea del archivo .env
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

# Crear una instancia para usar en todo el proyecto
settings = Settings()
```

### ¿Por qué usar `pydantic_settings`?

**Sin pydantic_settings (❌):**

```python
import os

# Tienes que convertir todo manualmente
DATABASE_URL = os.environ.get("DATABASE_URL")  # Puede ser None
PORT = int(os.environ.get("PORT", "8000"))      # Tienes que convertir a int
```

**Con pydantic_settings (✅):**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str    # Ya es string, garantizado
    PORT: int = 8000     # Ya es int, convertido automáticamente

# Si falta DATABASE_URL, ¡error claro al iniciar la app!
```

**Ventajas:**

1. **Tipos correctos:** `PORT` es `int`, no string
2. **Errores claros:** Si falta una variable obligatoria, te dice cuál
3. **Documentación:** Las variables están como atributos de clase
4. **Valores por defecto:** Puedes poner defaults fácilmente

---

## Paso 7: Conectar con la Base de Datos

### El archivo `app/database/connection.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..config import settings

# Crear el motor de conexión (el cable que conecta Python con MySQL)
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite es para pruebas (guarda en un archivo)
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}
    )
else:
    # MySQL es para producción
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,   # Verifica que la conexión esté viva
        pool_recycle=3600,    # Renueva la conexión cada hora
        pool_size=10,         # Mantiene 10 conexiones listas
        max_overflow=20       # Puede crear 20 más si hay mucha demanda
    )

# Crear la fábrica de sesiones (donde se crean las conexiones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La base para todos los modelos (como una plantilla)
Base = declarative_base()
```

### ¿Qué es un "pool de conexiones"?

Imagina que tienes un **call center** con 10 operadores:

```
┌─────────────────────────────────────────────────────┐
│                  POOL DE CONEXIONES                 │
├─────────────────────────────────────────────────────┤
│  👤 Operador 1    👤 Operador 2    👤 Operador 3    │
│  👤 Operador 4    👤 Operador 5    👤 Operador 6    │
│  👤 Operador 7    👤 Operador 8    👤 Operador 9    │
│  👤 Operador 10   (+ 20 más si hay emergencia)     │
└─────────────────────────────────────────────────────┘
```

Cuando alguien llama (hace una petición):
- Un operador disponible atiende
- Cuando termina, queda libre para la siguiente llamada
- Si llegan más de 10 llamadas, se pueden contratar 20 temporales

**Sin un pool:**
- Cada llamada contrata un nuevo operador (lento)
- Cada llamada termina y despide al operador (desperdicio)

**Con un pool:**
- Los operadores ya están contratados y esperando
- Rápido y eficiente

### ¿Por qué `autocommit=False`?

Imagina que estás haciendo una transferencia bancaria:

```
1. Sacar $100 de Juan
2. Poner $100 en María
```

**Con `autocommit=True` (❌):**
```
1. Sacar $100 de Juan    ← ¡Se guarda inmediatamente!
2. [ERROR] El sistema falla
3. Juan perdió $100, María no recibió nada  ← ¡Problema!
```

**Con `autocommit=False` (✅):**
```
1. Sacar $100 de Juan    ← Solo en memoria, no guardado
2. Poner $100 en María    ← Solo en memoria, no guardado
3. commit()               ← ¡Ahora sí se guarda todo junto!
4. Si hay error, rollback() ← Todo se deshace como si nada pasó
```

---

## Paso 8: ¡Ejecutar la Aplicación!

### El comando mágico

```bash
# Activa tu entorno virtual primero
.\.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate      # Mac/Linux

# Ejecuta la aplicación
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ¿Qué significa cada parte?

| Parte | Significado | Analogía |
|-------|-------------|----------|
| `uvicorn` | El servidor web | El mesero que lleva la comida |
| `app.main:app` | Tu aplicación | El restaurante |
| `--host 0.0.0.0` | Escucha en todas las redes | Abierto al público |
| `--port 8000` | El puerto | La dirección del local |
| `--reload` | Recarga cuando cambias código | Reinicia automáticamente |

### ¿Qué es `--reload`?

Es como tener un **ayudante mágico**:

```
Tú cambias el código → El ayudante ve el cambio → Reinicia automáticamente
```

Sin `--reload`:
```
Tú cambias el código → Tienes que parar todo → Reiniciar manualmente
```

**⚠️ Solo usa `--reload` en desarrollo. En producción, NO.**

---

## Paso 9: Verificar que Funciona

Abre tu navegador y ve a:

### La página principal
```
http://localhost:8000
```

Deberías ver algo como:
```json
{
  "mensaje": "Bienvenido a Liga Amateur App",
  "version": "v1",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### La documentación Swagger
```
http://localhost:8000/docs
```

Aquí puedes ver todos los endpoints de tu API y **probarlos** sin escribir código.

### La documentación ReDoc
```
http://localhost:8000/redoc
```

Una versión más bonita de la documentación.

---

## Solución de Problemas

### "No encuentro el módulo 'app'"

**¿Qué significa?**
Python no sabe dónde está tu código.

**Solución:**
```bash
# Asegúrate de estar en la carpeta correcta
cd backend

# Asegúrate de que el entorno virtual está activado
# Verás (.venv) al inicio de tu terminal
```

### "Can't connect to MySQL server"

**¿Qué significa?**
No puede conectar con la base de datos.

**Posibles causas:**

1. **MySQL no está corriendo**
   - Windows: Busca "Services" y asegúrate de que MySQL80 está activo
   - Mac: `brew services start mysql`

2. **Contraseña incorrecta**
   - Revisa tu archivo `.env`

3. **Puerto incorrecto**
   - MySQL usa el puerto 3306 por defecto

4. **Usuario sin permisos**
   - Asegúrate de haber creado el usuario con `GRANT ALL PRIVILEGES`

### "CORS blocked" (Error en el navegador)

**¿Qué significa?**
Tu frontend (la parte visual) está en un puerto diferente al backend (la parte lógica).

Por ejemplo:
- Frontend en `http://localhost:5173`
- Backend en `http://localhost:8000`

El navegador dice: "¡Son puertos diferentes! ¡Peligro!"

**Solución:**
En tu `.env`, agrega los orígenes permitidos:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:19006
```

### "Module not found"

**¿Qué significa?**
Falta instalar una librería.

**Solución:**
```bash
# Asegúrate de que el entorno virtual está activado
pip install -r requirements.txt
```

---

## Resumen

¡Felicidades! Has configurado todo. Aquí está lo que aprendiste:

1. **Entorno virtual** = Una caja de herramientas solo para este proyecto
2. **`requirements.txt`** = La lista de compras de librerías
3. **`.env`** = El archivo secreto con contraseñas y configuraciones
4. **MySQL** = La nevera gigante donde guardas datos
5. **Pool de conexiones** = Un equipo de operadores listos para atender
6. **`uvicorn`** = El mesero que sirve tu aplicación

**¿Listo para el siguiente paso?**

Ve a **02-arquitectura.md** para aprender cómo está organizado el código.