# CAMBIOS PENDIENTES EN API/BACKEND

**Fecha de extracción:** 11/03/2026
**Fuente:** Reuniones del proyecto (02/03, 09/03, 10/03)

---

## Índice

1. [Modificaciones en Tabla Usuarios](#1-modificaciones-en-tabla-usuarios)
2. [Nuevo Rol: Superadministrador](#2-nuevo-rol-superadministrador)
3. [Sistema de Imágenes](#3-sistema-de-imágenes)
4. [Configuración de Liga](#4-configuración-de-liga)
5. [Tabla Partido - Convocatoria](#5-tabla-partido---convocatoria)
6. [Flujo Crear Jugador](#6-flujo-crear-jugador)
7. [Sistema de Seguimiento](#7-sistema-de-seguimiento)
8. [Permisos para Delegados en Partidos](#8-permisos-para-delegados-en-partidos)
9. [Usuario No Registrado - Permisos](#9-usuario-no-registrado---permisos)
10. [Tareas Adicionales](#10-tareas-adicionales)

---

## 1. Modificaciones en Tabla Usuarios

### Campos a añadir

| Campo              | Tipo        | Descripción                                    | Estado    |
| ------------------ | ----------- | ---------------------------------------------- | --------- |
| `genero`           | ENUM        | Género del usuario (masculino, femenino, otro) | Pendiente |
| `telefono`         | VARCHAR(20) | Número de teléfono con validación de formato   | Pendiente |
| `fecha_nacimiento` | DATE        | Fecha de nacimiento del usuario                | Pendiente |


### Tareas Backend

- [ ] Crear migración Alembic para nuevos campos
- [ ] Actualizar modelo ORM (`backend/app/models/usuario.py`)
- [ ] Actualizar schemas Pydantic:
  - `UsuarioCreate`
  - `UsuarioUpdate`
  - `UsuarioResponse`
- [ ] Implementar validación de formato de teléfono (regex)
- [ ] Autoasignar `fecha_registro` en creación
- [ ] Actualizar endpoints afectados

### Archivos a modificar

```
backend/app/models/usuario.py
backend/app/schemas/usuario.py
backend/app/api/services/usuario_service.py
backend/app/database/init.sql
```

### Información a tener en cuenta
- los usuarios, cuando se registran, solo indican el nombre, el correo y la contraseña
- hay que actualizar el endpoint de edición para que cuando un usuario vea su información y quiera añadir esos datos, que pueda añadirlos

---

## 3. Sistema de Imágenes

### Arquitectura

**Almacenamiento:** Directorio local con URLs en base de datos
**Naming:** UUID para evitar colisiones

### Endpoints necesarios

| Método | Endpoint | Descripción | Autorización |
|--------|----------|-------------|---------------|
| POST | `/api/v1/imagenes/` | Subir imagen | Autenticado |
| GET | `/api/v1/imagenes/{id}` | Obtener imagen | Público |

### Validaciones

- Tipos permitidos: `image/jpeg`, `image/png`, `image/webp`
- Tamaño máximo: 5MB
- Sanitización de nombre de archivo

### Tareas Backend

- [ ] Crear modelo `Imagen` (opcional, o guardar URL en entidad)
- [ ] Crear endpoint de subida de imágenes
- [ ] Implementar validación de tipo y tamaño
- [ ] Configurar directorio de almacenamiento
- [ ] Añadir campo `imagen_url` en entidades necesarias:
  - `usuarios` (foto de perfil)
  - `equipos` (escudo)

### Archivos a crear/modificar

```
backend/app/api/routers/imagenes.py (nuevo)
backend/app/api/services/imagen_service.py (nuevo)
backend/app/config.py (añadir UPLOAD_DIR)
```

### Datos a tener en cuenta
- De esto, por ahora, no hay que tocar nada. cuando termines, planearemos como realizarlo
---

## 4. Configuración de Liga

### Nueva tabla `liga_configuracion`

```sql
CREATE TABLE liga_configuracion (
    id_configuracion INT AUTO_INCREMENT PRIMARY KEY,
    id_liga INT NOT NULL UNIQUE,
    hora_partidos TIME NOT NULL DEFAULT '17:00:00',
    max_equipos INT NOT NULL DEFAULT 20,
    min_jugadores_equipo INT NOT NULL DEFAULT 7,
    min_partidos_entre_equipos INT NOT NULL DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_liga) REFERENCES ligas(id_liga) ON DELETE CASCADE
);
```

### Endpoints necesarios

| Método | Endpoint | Descripción | Autorización |
|--------|----------|-------------|---------------|
| GET | `/api/v1/ligas/{id}/configuracion` | Obtener configuración | Público |
| PUT | `/api/v1/ligas/{id}/configuracion` | Actualizar configuración | admin/superadmin |

### Tareas Backend

- [ ] Crear modelo `LigaConfiguracion`
- [ ] Crear schema Pydantic
- [ ] Crear router y service
- [ ] Crear migración
- [ ] Auto-crear configuración al crear una liga

### Archivos a crear/modificar

```
backend/app/models/liga_configuracion.py (nuevo)
backend/app/schemas/liga_configuracion.py (nuevo)
backend/app/api/routers/liga_configuracion.py (nuevo)
backend/app/api/services/liga_configuracion_service.py (nuevo)
```

---

## 5. Tabla Partido - Convocatoria

### Descripción

Añadir sistema de convocatoria para partidos. Los jugadores pueden ser convocados a un partido.

### Estructura propuesta

```sql
CREATE TABLE convocatoria (
    id_convocatoria INT AUTO_INCREMENT PRIMARY KEY,
    id_partido INT NOT NULL,
    id_jugador INT NOT NULL,
    estado ENUM('convocado', 'confirmado', 'ausente') NOT NULL DEFAULT 'convocado',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partido) REFERENCES partidos(id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
    UNIQUE KEY unique_convocatoria (id_partido, id_jugador)
);
```

### Tareas Backend

- [ ] Definir estructura de datos final
- [ ] Crear modelo `Convocatoria`
- [ ] Crear endpoints para gestionar convocatoria
- [ ] Validar que solo entrenador/delegado pueda convocar

### Archivos a crear

```
backend/app/models/convocatoria.py (nuevo)
backend/app/schemas/convocatoria.py (nuevo)
backend/app/api/routers/convocatoria.py (nuevo)
backend/app/api/services/convocatoria_service.py (nuevo)
```

---

## 6. Flujo Crear Jugador

### Endpoints necesarios

| Método | Endpoint | Descripción | Autorización |
|--------|----------|-------------|---------------|
| GET | `/api/v1/usuarios/buscar?email={email}` | Buscar usuario por email | coach/delegate |
| POST | `/api/v1/jugadores/` | Crear jugador | coach/delegate |

### Flujo

1. Entrenador/Delegado busca usuario por email
2. Si existe → Lo selecciona para crear jugador
3. Si no existe → Redirige a registro de usuario

### Tareas Backend

- [ ] Crear endpoint de búsqueda de usuario
- [ ] Validar que el usuario no tenga ya un jugador asociado
- [ ] Validar que el equipo pertenece a la liga del entrenador/delegado

### Datos a tener en cuenta
Por ahora, no tener en cuenta

---

## 7. Sistema de Seguimiento

### Descripción

Los usuarios pueden seguir equipos para recibir notificaciones y actualizaciones.

### Prioridad

1. Seguir equipo (implementar primero)
2. Seguir liga (si hay tiempo)

### Tabla propuesta

```sql
CREATE TABLE usuario_sigue_equipo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_equipo INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    UNIQUE KEY unique_seguimiento (id_usuario, id_equipo)
);
```

### Endpoints necesarios

| Método | Endpoint | Descripción | Autorización |
|--------|----------|-------------|---------------|
| POST | `/api/v1/usuarios/me/seguir-equipo/{equipo_id}` | Seguir equipo | Autenticado |
| DELETE | `/api/v1/usuarios/me/seguir-equipo/{equipo_id}` | Dejar de seguir | Autenticado |
| GET | `/api/v1/usuarios/me/equipos-seguidos` | Listar equipos seguidos | Autenticado |
### Datos a tener en cuenta
Por ahora, no tener en cuenta     

---

## 8. Permisos para Delegados en Partidos

### Regla de negocio

> **Solo el delegado del equipo local puede añadir eventos del partido.**
> Al delegado del equipo visitante NO debe aparecerle la opción de añadir eventos.

### Cambios necesarios

- [ ] Modificar endpoint `POST /api/v1/eventos/` para validar:
  - El usuario debe tener rol `delegate`
  - El usuario debe ser delegado del equipo LOCAL del partido
- [ ] Añadir validación en el servicio

### Implementación

```python
# En evento_service.py
def crear_evento(db, evento_data, usuario_actual):
    partido = obtener_partido(db, evento_data.id_partido)

    # Verificar que el usuario es delegado del equipo local
    equipo_local = partido.equipo_local
    if equipo_local.id_delegado != usuario_actual.id_usuario:
        raise ValueError("Solo el delegado del equipo local puede añadir eventos")

    # Crear evento...
```

---

## 9. Usuario No Registrado - Permisos

### Permisos públicos (sin autenticación)

| Recurso       | Acceso                        | Endpoints                             |
| ------------- | ----------------------------- | ------------------------------------- |
| Ligas         | Listar y ver detalles         | `GET /ligas/`, `GET /ligas/{id}`      |
| Equipos       | Listar y ver detalles básicos | `GET /equipos/`, `GET /equipos/{id}`  |
| Partidos      | Resultados y programación     | `GET /partidos/` (solo datos básicos) |
| Clasificación | Ver clasificación             | Endpoint a crear                      |


### Permisos restringidos (requiere autenticación)

| Recurso | Restricción |
|---------|-------------|
| Información detallada de equipos | Solo usuarios autenticados |
| Información de jugadores | Solo usuarios autenticados |
| Información detallada de partidos | Solo usuarios autenticados |
| Perfil de usuario | Solo el propio usuario |

### Endpoints públicos a crear

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/public/clasificacion/{liga_id}` | Clasificación de una liga |
| GET | `/api/v1/public/jornada/{liga_id}/{jornada}` | Partidos de una jornada |
### Datos a tener en cuenta
Por ahora no tener en cuenta

---

## Resumen de Archivos a Crear

```
backend/app/models/
├── liga_configuracion.py (nuevo)
├── convocatoria.py (nuevo)
├── seguimiento.py (nuevo)
└── imagen.py (nuevo, opcional)

backend/app/schemas/
├── liga_configuracion.py (nuevo)
├── convocatoria.py (nuevo)
├── seguimiento.py (nuevo)
└── imagen.py (nuevo)

backend/app/api/routers/
├── liga_configuracion.py (nuevo)
├── convocatoria.py (nuevo)
├── seguimiento.py (nuevo)
├── imagen.py (nuevo)
└── public.py (nuevo)

backend/app/api/services/
├── liga_configuracion_service.py (nuevo)
├── convocatoria_service.py (nuevo)
├── seguimiento_service.py (nuevo)
└── imagen_service.py (nuevo)
```

## Resumen de Archivos a Modificar

```
backend/app/models/usuario.py
backend/app/schemas/usuario.py
backend/app/api/services/usuario_service.py
backend/app/api/services/evento_service.py
backend/app/api/dependencies.py
backend/app/database/init.sql
backend/app/config.py
```

---

## Prioridad de Implementación Sugerida

1. **Alta prioridad**
   - Modificaciones en tabla usuarios (campos básicos)
   - Nuevo rol superadmin
   - Permisos para delegados en partidos

2. **Media prioridad**
   - Sistema de imágenes
   - Configuración de liga
   - Flujo crear jugador

3. **Baja prioridad**
   - Convocatoria de partidos
   - Sistema de seguimiento
   - Endpoints públicos adicionales

---

*Documento generado automáticamente a partir de las actas de reuniones del proyecto.*