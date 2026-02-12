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
│   ├── .env                    # Variables de entorno (NO subir a Git)
│   ├── .env.example            # Plantilla de configuración
│   ├── requirements.txt        # Dependencias Python
│   └── app/
│       ├── main.py             # Punto de entrada de la aplicación
│       ├── config.py           # Configuración centralizada
│       ├── api/
│       │   ├── dependencies.py # Autenticación y dependencias
│       │   ├── routers/        # Endpoints REST (10 routers)
│       │   │   ├── auth.py
│       │   │   ├── usuarios.py
│       │   │   ├── roles.py
│       │   │   ├── ligas.py
│       │   │   ├── equipos.py
│       │   │   ├── jugadores.py
│       │   │   ├── partidos.py
│       │   │   ├── eventos.py
│       │   │   ├── formaciones.py
│       │   │   └── notificaciones.py
│       │   └── services/       # Lógica de negocio (9 services)
│       │       ├── usuario_service.py
│       │       ├── rol_service.py
│       │       ├── liga_service.py
│       │       ├── equipo_service.py
│       │       ├── jugador_service.py
│       │       ├── partido_service.py
│       │       ├── evento_service.py
│       │       ├── formacion_service.py
│       │       └── notificacion_service.py
│       ├── models/              # Modelos ORM SQLAlchemy (13 modelos)
│       │   ├── usuario.py
│       │   ├── rol.py
│       │   ├── usuario_rol.py
│       │   ├── liga.py
│       │   ├── equipo.py
│       │   ├── jugador.py
│       │   ├── partido.py
│       │   ├── evento_partido.py
│       │   ├── formacion.py
│       │   ├── posicion_formacion.py
│       │   ├── formacion_equipo.py
│       │   ├── formacion_partido.py
│       │   └── notificacion.py
│       ├── schemas/             # Schemas Pydantic (13 schemas)
│       │   ├── usuario.py
│       │   ├── rol.py
│       │   ├── usuario_rol.py
│       │   ├── liga.py
│       │   ├── equipo.py
│       │   ├── jugador.py
│       │   ├── partido.py
│       │   ├── evento_partido.py
│       │   ├── formacion.py
│       │   ├── posicion_formacion.py
│       │   ├── formacion_equipo.py
│       │   ├── formacion_partido.py
│       │   └── notificacion.py
│       └── database/
│           ├── connection.py   # Configuración SQLAlchemy
│           └── init.sql        # Script de inicialización DB
├── .gitignore
├── AGENTS.md                   # Guía para Verdent AI
└── README.md                   # Este archivo
```

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

- Python 3.10 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes Python)

### 2. Clonar el Repositorio

```bash
git clone https://github.com/1DAM-antoniocue491/GoalApp.git
cd GoalApp
```

### 3. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

#### Crear la base de datos en MySQL:

```sql
mysql -u <user> -p
CREATE DATABASE futbol_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Ejecutar script de inicialización:

```bash
mysql -u <user> -p futbol_app < app/database/init.sql
```

### 5. Configurar Variables de Entorno

El archivo `.env` ya está creado en `backend/.env`. Solo necesitas editar las credenciales:

```bash
# Editar el archivo .env
notepad .env  # Windows
nano .env     # Linux/Mac
```

Cambia la línea de `DATABASE_URL` con tus credenciales:

```env
DATABASE_URL=mysql+pymysql://tu_usuario:tu_password@localhost:3306/futbol_app
```

**Nota:** El archivo `.env` contiene una SECRET_KEY segura ya generada. No la cambies a menos que sea necesario.

### 6. Iniciar el Servidor

```bash
# Asegúrate de estar en el directorio backend/
python app/main.py
```

O alternativamente:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

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
