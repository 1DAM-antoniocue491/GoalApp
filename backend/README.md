# Backend – Liga Amateur App

## 1. Descripción

El backend de la aplicación **Liga Amateur App** está desarrollado con **FastAPI** y se encarga de:
- Gestionar usuarios, roles y permisos
- Administrar ligas, equipos, jugadores y partidos
- Registrar eventos de partidos (goles, tarjetas, cambios…)
- Controlar formaciones y alineaciones
- Proveer una **API REST** para que el frontend (móvil y web) consuma los datos
- Garantizar seguridad, integridad y consistencia de la base de datos

---
## 2. Tecnologías

- **Python 3.10+**
- **FastAPI** (Framework web y API)
- **SQLAlchemy** (ORM para la base de datos)
- **MySQL** (Base de datos relacional)
- **Alembic** (Migraciones de base de datos)

---
## 3. Estructura de carpetas

```
backend/
├── app/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── usuarios.py
│   │   │   ├── roles.py
│   │   │   ├── equipos.py
│   │   │   ├── jugadores.py
│   │   │   ├── ligas.py
│   │   │   ├── partidos.py
│   │   │   ├── eventos.py
│   │   │   ├── formaciones.py
│   │   │   └── notificaciones.py
│   │   │
│   │   ├── services/
│   │   │   ├── usuario_service.py
│   │   │   ├── rol_service.py
│   │   │   ├── equipo_service.py
│   │   │   ├── jugador_service.py
│   │   │   ├── liga_service.py
│   │   │   ├── partido_service.py
│   │   │   ├── evento_service.py
│   │   │   ├── formacion_service.py
│   │   │   └── notificacion_service.py
│   │   │
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── rol.py
│   │   ├── usuario_rol.py
│   │   ├── liga.py
│   │   ├── equipo.py
│   │   ├── jugador.py
│   │   ├── partido.py
│   │   ├── evento_partido.py
│   │   ├── formacion.py
│   │   ├── posicion_formacion.py
│   │   ├── formacion_equipo.py
│   │   ├── formacion_partido.py
│   │   └── notificacion.py
│   │
│   ├── schemas/
│   │   ├── usuario.py
│   │   ├── rol.py
│   │   ├── equipo.py
│   │   ├── jugador.py
│   │   ├── liga.py
│   │   ├── partido.py
│   │   ├── evento.py
│   │   ├── formacion.py
│   │   ├── alineacion.py
│   │   └── notificacion.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── init.sql
│   │   └── migrations/
│   │
│   └── main.py
│
├── requirements.txt
└── README.md
```

---

## 4. Explicación de carpetas

|Carpeta/Fichero|Contenido / Función|
|---|---|
|`api/endpoints/`|Archivos con rutas REST para cada recurso (usuarios, equipos, partidos…).|
|`api/dependencies.py`|Funciones de autenticación, autorización y sesión de base de datos.|
|`models/`|Modelos ORM que representan las tablas de la base de datos y relaciones.|
|`schemas/`|Validación y serialización de datos (Pydantic schemas).|
|`database/`|Conexión, scripts iniciales y migraciones de la base de datos.|
|`main.py`|Inicializa FastAPI, registra routers y configura middlewares.|


---

## 5. Uso de la API

- Todos los endpoints están en `app/api/endpoints/`
- Se recomienda autenticación mediante token JWT
- Ejemplo de endpoints principales:
    - `/usuarios/` → gestión de usuarios
    - `/equipos/` → gestión de equipos
    - `/partidos/` → registro de partidos
    - `/eventos/` → registrar goles, tarjetas y cambios
    - `/formaciones/` → gestionar formaciones y alineaciones

---

## 6. Notas

- Mantener **nombres de columnas en español** coherentes con la base de datos
- Separación clara entre **models**, **schemas** y **endpoints**
- Validación y permisos aplicados en **dependencies.py**
- Seguir buenas prácticas de desarrollo y commits claros