# ⚽ GoalApp - Liga Amateur

API REST para la gestión completa de ligas de fútbol amateur.

## 📋 Descripción

Aplicación backend desarrollada con FastAPI para gestionar ligas de fútbol amateur, incluyendo equipos, jugadores, partidos, estadísticas y formaciones tácticas.

### Características principales

- ✅ Gestión de usuarios con sistema de roles (Admin, Coach, Delegate, Player, Viewer)
- ✅ Gestión de ligas, equipos y jugadores
- ✅ Registro de partidos y eventos en tiempo real (goles, tarjetas, cambios, MVP)
- ✅ Formaciones tácticas y alineaciones
- ✅ Sistema de notificaciones
- ✅ Autenticación JWT con tokens seguros
- ✅ Documentación automática con Swagger/OpenAPI

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy
- **Base de Datos**: MySQL
- **Autenticación**: JWT (python-jose, passlib)
- **Validación**: Pydantic
- **Servidor**: Uvicorn

## 📁 Estructura del Proyecto

```
GoalApp/
├── backend/
│   ├── .env.example            # Plantilla de configuración
│   ├── requirements.txt        # Dependencias Python
│   └── app/
│       ├── main.py             # Punto de entrada de la aplicación
│       ├── config.py           # Configuración centralizada
│       ├── api/
│       │   ├── dependencies.py # Autenticación y dependencias
│       │   ├── routers/        # Endpoints REST (10 routers)
│       │   └── services/       # Lógica de negocio (9 services)
│       ├── models/             # Modelos ORM SQLAlchemy (13 modelos)
│       ├── schemas/            # Schemas Pydantic (13 schemas)
│       └── database/
├── .gitignore
└── README.md                   # Este archivo
```

## 🚀 Instalación y Configuración (Actualizada)

Esta guía está pensada para que puedas poner en marcha **GoalApp** tanto en **Windows** como en **Ubuntu** (Linux) usando un **entorno virtual** y con los últimos ajustes necesarios (bcrypt, variables de entorno, puertos, etc.).

> **Requisitos mínimos**
> 
> - Python ≥ 3.10 (idealmente 3.13, que es la versión que tienes instalada)
> - MySQL ≥ 8.0
> - `git` (para clonar el repo)
> - `pip` (gestor de paquetes)

---

### 1️⃣ Preparar el entorno del proyecto

#### a) Clonar el repositorio

``` bash
git clone https://github.com/1DAM-antoniocue491/GoalApp.git
cd GoalApp/backend
```
#### b) Crear y activar un entorno virtual

``` PowerShell
--- Ubuntu / Linux ---------------------------------------
python3 -m venv .venv # crear el entorno (solo la 1ª vez)
source .venv/bin/activate # activar

--- Windows PowerShell ----------------------------------- python -m venv .venv # crear el entorno (solo la 1ª vez)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass # permite scripts
.\.venv\Scripts\Activate.ps1 # activar
```

> Cuando el entorno está activo el prompt mostrará `(.venv)` al inicio.

#### c) Actualizar `pip` e instalar dependencias

``` python
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

> **Problemas con `bcrypt` o `cryptography`**  
> En Ubuntu instala los paquetes de compilación antes de `pip install`:

``` bash
sudo apt update
sudo apt install -y build-essential libffi-dev libssl-dev python3-dev
```

> En Windows asegúrate de tener **Microsoft Visual C++ Build Tools** instalados (el instalador de Visual Studio Community incluye la opción _Desktop development with C++_).

---

### 2️⃣ Configurar la base de datos MySQL

#### a) Crear la base de datos

``` mysql
-- Desde la consola MySQL
mysql -u <usuario> -p CREATE DATABASE futbol_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
#### b) Ejecutar el script de inicialización

``` bash
mysql -u <usuario> -p futbol_app < app/database/init.sql
```

> El script crea las tablas `usuarios`, `roles`, `usuario_rol`, etc.

---

### 3️⃣ Variables de entorno (`.env`)

El proyecto ya incluye un archivo `backend/.env.example`.

> **Importante:** Debes renombrar el fichero `.env.example` y ponerle el nombre de `.env`, si no, no se podrán obtener los datos.

Edítalo para añadir tus credenciales de base de datos y, si lo deseas, cambiar la clave secreta.

``` bash
# Windows
notepad .env
# Linux / macOS
nano .env
```

> **Importante:** `HOST=0.0.0.0` permite que la API sea accesible desde otros equipos de la red.

---

### 4️⃣ Abrir el puerto 8000 (si usas firewall)

#### Windows (PowerShell)

``` PowerShell
New-NetFirewallRule -DisplayName "GoalApp API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```
#### Ubuntu (UFW)

``` bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

> Si utilizas otro firewall (iptables, firewalld, etc.) abre el puerto de forma equivalente.

---

### 5️⃣ Lanzar el servidor

Con el entorno virtual **activo** y el archivo `.env` configurado:

**Opción 1:** usando Uvicorn (recomendado, permite hot‑reload)
``` python
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- `--reload` recarga automáticamente el servidor cuando cambias código (solo para desarrollo).
- En producción elimina `--reload` y considera usar un servidor ASGI como **Gunicorn** detrás de **Nginx** o **Caddy**.

**Opción 2:** usando el script incluido (para desarrollo rápido)
``` python
python app/main.py
```

**URL de la API**

```
http://<IP_DE_TU_MÁQUINA>:8000
```

- En la misma máquina: `http://localhost:8000`
- Desde otro equipo de la red: sustituye `<IP_DE_TU_MÁQUINA>` por la dirección IPv4 que obtengas con `ipconfig` (Windows) o `ip a` (Linux).

## 🧪 Probar la API

### 1. Documentación Interactiva (Swagger UI)

Abre en tu navegador:

```
http://localhost:8000/docs
```

Aquí podrás:
- Ver todos los endpoints disponibles
- Probar cada endpoint directamente desde el navegador
- Ver los esquemas de datos de entrada/salida
- Autenticarte y obtener un token JWT

### 2. Documentación Alternativa (ReDoc)

```
http://localhost:8000/redoc
```

### 3. Health Check

Verifica que el servidor esté funcionando:

```
http://localhost:8000/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "app": "Liga Amateur App",
  "version": "v1",
  "environment": "development"
}
```

### 4. Endpoint Raíz

```
http://localhost:8000/
```

Respuesta:
```json
{
  "mensaje": "Bienvenido a Liga Amateur App",
  "version": "v1",
  "entorno": "development",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

## 🔑 Autenticación

### 1. Crear un Usuario (Registro)

**Endpoint:** `POST /api/v1/usuarios/`

**Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "contraseña": "password123"
}
```

### 2. Iniciar Sesión (Login)

**Endpoint:** `POST /api/v1/auth/login`

**Body (form-data):**
```
username: juan@example.com
password: password123
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Usar el Token

En Swagger UI:
1. Copia el `access_token`
2. Haz clic en el botón **"Authorize"** (🔒)
3. Pega el token en el campo
4. Haz clic en "Authorize"

En peticiones directas (curl, Postman, etc.):
```bash
Authorization: Bearer <tu_token_aqui>
```

## 📚 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Refrescar token
- `GET /api/v1/auth/me` - Obtener usuario actual

### Usuarios
- `POST /api/v1/usuarios/` - Crear usuario
- `GET /api/v1/usuarios/` - Listar usuarios
- `GET /api/v1/usuarios/{id}` - Obtener usuario
- `PUT /api/v1/usuarios/{id}` - Actualizar usuario
- `DELETE /api/v1/usuarios/{id}` - Eliminar usuario

### Ligas
- `POST /api/v1/ligas/` - Crear liga
- `GET /api/v1/ligas/` - Listar ligas
- `GET /api/v1/ligas/{id}` - Obtener liga
- `PUT /api/v1/ligas/{id}` - Actualizar liga
- `DELETE /api/v1/ligas/{id}` - Eliminar liga

### Equipos
- `POST /api/v1/equipos/` - Crear equipo
- `GET /api/v1/equipos/` - Listar equipos
- `GET /api/v1/equipos/{id}` - Obtener equipo
- `PUT /api/v1/equipos/{id}` - Actualizar equipo
- `DELETE /api/v1/equipos/{id}` - Eliminar equipo

### Jugadores
- `POST /api/v1/jugadores/` - Crear jugador
- `GET /api/v1/jugadores/` - Listar jugadores
- `GET /api/v1/jugadores/{id}` - Obtener jugador
- `PUT /api/v1/jugadores/{id}` - Actualizar jugador
- `DELETE /api/v1/jugadores/{id}` - Eliminar jugador

### Partidos
- `POST /api/v1/partidos/` - Crear partido
- `GET /api/v1/partidos/` - Listar partidos
- `GET /api/v1/partidos/{id}` - Obtener partido
- `PUT /api/v1/partidos/{id}` - Actualizar partido
- `DELETE /api/v1/partidos/{id}` - Eliminar partido

### Eventos (Goles, Tarjetas, etc.)
- `POST /api/v1/eventos/` - Crear evento
- `GET /api/v1/eventos/partido/{id_partido}` - Listar eventos de un partido

Ver documentación completa en `/docs`

## 🔐 Sistema de Roles

| Rol | Permisos |
|-----|----------|
| **Admin** | Gestión global de ligas, equipos y usuarios |
| **Coach** | Gestión de su equipo y alineaciones |
| **Delegate** | Registro de eventos en partidos |
| **Player** | Consulta de información y estadísticas propias |
| **Viewer** | Consulta de información pública |

## ⚙️ Configuración Avanzada

### Variables de Entorno

Todas las variables se configuran en `backend/.env`:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | Conexión a MySQL | `mysql+pymysql://root:password@localhost:3306/futbol_app` |
| `DATABASE_ECHO` | Mostrar queries SQL | `True` |
| `SECRET_KEY` | Clave para JWT | (Generada automáticamente) |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración token | `60` |
| `ENVIRONMENT` | Entorno | `development` |
| `PORT` | Puerto servidor | `8000` |
| `CORS_ORIGINS` | Orígenes permitidos | `http://localhost:3000,...` |

### Cambiar Puerto

Edita `backend/.env`:
```env
PORT=5000
```

### Modo Producción

Edita `backend/.env`:
```env
ENVIRONMENT=production
DATABASE_ECHO=False
```

## 🐛 Solución de Problemas

### Error: "Field required"
**Problema:** Falta una variable en `.env`

**Solución:** Compara tu `.env` con `.env.example` y añade las variables faltantes

### Error: "Can't connect to MySQL server"
**Problema:** MySQL no está corriendo o credenciales incorrectas

**Solución:**
1. Verifica que MySQL esté corriendo: `mysql --version`
2. Verifica credenciales en `DATABASE_URL`
3. Verifica que la base de datos `futbol_app` exista

### Error: "ModuleNotFoundError"
**Problema:** Dependencias no instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

### Puerto 8000 en uso
**Problema:** Otro proceso está usando el puerto

**Solución:**
- Cambiar puerto en `.env`: `PORT=5000`
- O matar el proceso: `netstat -ano | findstr :8000` (Windows)

## 📝 Notas de Desarrollo

- El código está completamente documentado con docstrings en español
- Todos los nombres de variables y tablas están en español
- Se sigue el patrón de arquitectura en capas (routers → services → models)
- La autenticación es obligatoria para la mayoría de endpoints

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

## 📄 Licencia

Este proyecto es parte de un trabajo académico.

## 👥 Autor

Proyecto desarrollado para la gestión de ligas de fútbol amateur.

## 📞 Soporte

Para problemas o preguntas, consulta la documentación en `/docs` o revisa el archivo `AGENTS.md` para guías de desarrollo.
