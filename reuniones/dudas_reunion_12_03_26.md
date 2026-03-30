# DUDAS REUNIÓN 12/03/26

**Fecha:** 12 de marzo de 2026
**Estado:** Pendientes de implementar

---

## Resumen

En la reunión del 10/03/26 se identificaron varias tareas para el backend. Este documento recoge las que **NO se han implementado** todavía y quedan pendientes para futuras sesiones.

---

## 1. Sistema de Imágenes

**Estado:** ❌ NO implementado

**Nota del equipo:** *"De esto, por ahora, no hay que tocar nada. Cuando termines, planearemos cómo realizarlo"*

### Tareas pendientes

| Tarea | Descripción |
|-------|-------------|
| Definir arquitectura | Decidir entre almacenamiento local vs S3 |
| Endpoint subida imagen | `POST /api/v1/imagenes/` |
| Endpoint obtener imagen | `GET /api/v1/imagenes/{id}` |
| Validaciones | Tipo de archivo (jpeg, png, webp), tamaño máximo (5MB) |
| Añadir campo `imagen_url` | En entidades `usuarios` y `equipos` |

### Archivos a crear

```
backend/app/api/routers/imagenes.py
backend/app/api/services/imagen_service.py
backend/app/config.py (añadir UPLOAD_DIR)
```

---

## 2. Flujo Crear Jugador

**Estado:** ❌ NO implementado

**Nota del equipo:** *"Por ahora, no tener en cuenta"*

### Tareas pendientes

| Tarea | Descripción |
|-------|-------------|
| Endpoint búsqueda usuario | `GET /api/v1/usuarios/buscar?email={email}` |
| Validación duplicados | Verificar que el usuario no tenga ya un jugador asociado |
| Validación equipo-liga | Verificar que el equipo pertenece a la liga del entrenador/delegado |

### Flujo esperado

1. Entrenador/Delegado busca usuario por email
2. Si existe → Lo selecciona para crear jugador
3. Si no existe → Redirige a registro de usuario

---

## 3. Sistema de Seguimiento

**Estado:** ❌ NO implementado

**Nota del equipo:** *"Por ahora, no tener en cuenta"*

### Tareas pendientes

| Tarea | Descripción |
|-------|-------------|
| Crear tabla `usuario_sigue_equipo` | Relación N:N entre usuarios y equipos |
| Endpoint seguir equipo | `POST /api/v1/usuarios/me/seguir-equipo/{equipo_id}` |
| Endpoint dejar de seguir | `DELETE /api/v1/usuarios/me/seguir-equipo/{equipo_id}` |
| Endpoint listar seguidos | `GET /api/v1/usuarios/me/equipos-seguidos` |

### Archivos a crear

```
backend/app/models/seguimiento.py
backend/app/schemas/seguimiento.py
backend/app/api/routers/seguimiento.py
backend/app/api/services/seguimiento_service.py
```

---

## 4. Usuario No Registrado - Permisos

**Estado:** ❌ NO implementado

**Nota del equipo:** *"Por ahora no tener en cuenta"*

### Tareas pendientes

| Tarea | Descripción |
|-------|-------------|
| Endpoint clasificación pública | `GET /api/v1/public/clasificacion/{liga_id}` |
| Endpoint jornada pública | `GET /api/v1/public/jornada/{liga_id}/{jornada}` |
| Limitar información | Restringir datos detallados a usuarios autenticados |

### Permisos públicos actuales

| Recurso | Estado actual |
|---------|---------------|
| Ligas | ✅ Público (listar y ver) |
| Equipos | ✅ Público (listar y ver) |
| Partidos | ✅ Público (listar) |
| Clasificación | ❌ Pendiente |

---

## 5. Tabla Partido - Convocatoria

**Estado:** ❌ NO implementado

### Tareas pendientes

| Tarea | Descripción |
|-------|-------------|
| Definir estructura | Confirmar diseño final de la tabla `convocatoria` |
| Crear modelo | `backend/app/models/convocatoria.py` |
| Crear schema | `backend/app/schemas/convocatoria.py` |
| Crear endpoints | CRUD de convocatoria |
| Validación | Solo entrenador/delegado puede convocar |

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

---

## 6. Rol Superadministrador

**Estado:** ❌ NO implementado

**Nota del equipo:** *"No lo modifiques, o sea, que no crees nada de eso todavía"*

### Tareas pendientes

| Tarea | Descripción |
|-------|-------------|
| Añadir rol `superadmin` | En seeds iniciales |
| Middleware de autorización | Distinguir admin de superadmin |
| Gestión de permisos | Endpoint para que superadmin gestione permisos de roles |

### Funcionalidades del superadmin

| Funcionalidad | admin | superadmin |
|---------------|-------|------------|
| Gestionar ligas | ✅ | ✅ |
| Gestionar equipos | ✅ | ✅ |
| Gestionar usuarios | ✅ | ✅ |
| Gestionar permisos de roles | ❌ | ✅ |
| Gestionar roles | ❌ | ✅ |

---

## Resumen de Prioridad

| Prioridad | Tarea | Nota |
|----------|------|------|
| 🔴 Alta | - | Todas las de alta prioridad ya implementadas |
| 🟡 Media | Sistema de imágenes | Esperar a planificación |
| 🟡 Media | Flujo crear jugador | Esperar indicaciones |
| 🟡 Media | Configuración de liga | ✅ Ya implementado |
| 🟢 Baja | Sistema de seguimiento | Esperar |
| 🟢 Baja | Usuario no registrado | Esperar |
| 🟢 Baja | Convocatoria | Baja prioridad |
| 🟢 Baja | Superadmin | Esperar |

---

## Próximos Pasos Sugeridos

1. **Esperar reunión con el equipo** para planificar el sistema de imágenes
2. **Definir flujo de crear jugador** cuando se implemente el frontend
3. **Analizar qué endpoints públicos** son necesarios para usuarios no registrados

---

*Documento generado a partir de CAMBIOS_PENDIENTES_BACKEND.md*