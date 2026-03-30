# Documentación del Backend GoalApp

## Descripción

GoalApp es una aplicación para gestionar ligas de fútbol amateur. El backend está construido con FastAPI (Python) y proporciona una API REST con autenticación JWT.

## Estructura de la Documentación

| Archivo | Contenido |
|---------|-----------|
| [01-instalacion-configuracion.md](./01-instalacion-configuracion.md) | Instalación, configuración de entorno y ejecución |
| [02-arquitectura.md](./02-arquitectura.md) | Estructura de carpetas y responsabilidades de cada capa |
| [03-base-datos.md](./03-base-datos.md) | Modelos ORM, SQLAlchemy y relaciones |
| [04-schemas.md](./04-schemas.md) | Validación de datos con Pydantic |
| [05-servicios.md](./05-servicios.md) | Capa de lógica de negocio |
| [06-routers.md](./06-routers.md) | Endpoints REST y documentación automática |
| [07-autenticacion.md](./07-autenticacion.md) | Sistema de autenticación JWT |
| [08-testing.md](./08-testing.md) | Pruebas automatizadas con pytest |
| [09-despliegue.md](./09-despliegue.md) | Despliegue en producción |

## Stack Tecnológico

```
┌─────────────────────────────────────────────┐
│                 FastAPI                     │
│         (Framework Web en Python)           │
├─────────────────────────────────────────────┤
│              SQLAlchemy (ORM)               │
│         (Mapeo objeto-relacional)           │
├─────────────────────────────────────────────┤
│              MySQL / SQLite                 │
│              (Base de datos)                │
└─────────────────────────────────────────────┘
```

### Dependencias principales

| Librería | Propósito |
|----------|-----------|
| `fastapi` | Framework web |
| `uvicorn` | Servidor ASGI |
| `sqlalchemy` | ORM para base de datos |
| `pymysql` | Driver de MySQL |
| `pydantic` | Validación de datos |
| `python-jose` | Tokens JWT |
| `passlib[bcrypt]` | Hash de contraseñas |

## Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                  │
│                    (Routers / Endpoints)                 │
├─────────────────────────────────────────────────────────┤
│                    CAPA DE LÓGICA                        │
│                    (Services)                            │
├─────────────────────────────────────────────────────────┤
│                    CAPA DE DATOS                         │
│                    (Models / ORM)                        │
├─────────────────────────────────────────────────────────┤
│                    BASE DE DATOS                         │
│                    (MySQL)                               │
└─────────────────────────────────────────────────────────┘
```

## Flujo de una Petición HTTP

```
Cliente → Router → Service → Model → Base de datos
                    ↓
              Validación (Schema)
```

## Convenciones del Proyecto

- **Idioma**: Código comentado en español
- **Nombres**: Variables y funciones en español (`obtener_usuario`)
- **Tablas**: En plural (`usuarios`, `equipos`, `ligas`)
- **Claves primarias**: Prefijo `id_` (`id_usuario`, `id_equipo`)

## Enlaces Externos

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación de Pydantic](https://docs.pydantic.dev/)