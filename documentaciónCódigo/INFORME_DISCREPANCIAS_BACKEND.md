# Informe de Discrepancias: Documentación vs Implementación

**Fecha de análisis:** 2026-03-25
**Proyecto:** GoalApp - Gestión de Ligas Amateur de Fútbol
**Alcance:** Análisis exhaustivo de reglas de negocio documentadas vs implementadas en el backend

---

## Resumen Ejecutivo

Este informe documenta las discrepancias encontradas entre las reglas de negocio descritas en la documentación (`/doc`) y la implementación actual del backend (`/backend`). El análisis revela que **aproximadamente el 60% de las reglas de negocio documentadas NO están implementadas** en el código.

### Hallazgos Principales

| Categoría | Reglas Documentadas | Reglas Implementadas | Porcentaje |
|-----------|---------------------|----------------------|------------|
| Estados de Liga | 4 estados + transiciones | Solo booleano `activa` | 0% |
| Asignación de Roles | Automática por participación | No implementada | 0% |
| Restricciones de Unicidad | Múltiples (entrenador, jugador) | No implementadas | 0% |
| Validaciones de Eventos | 6 reglas | 3 reglas | 50% |
| Validaciones de Partidos | 5 reglas | 0 reglas | 0% |
| Permisos RBAC | Básicos | Implementados | 100% |

---

## 1. Estados de Liga

### Documentación (`doc/reglas-y-convenciones/gestion-de-ligas.md`)

La documentación define un ciclo de vida de liga con **4 estados**:

```
CREADA → CONFIGURACIÓN → EN COMPETICIÓN → FINALIZADA
```

**Reglas de transición documentadas:**

| Transición | Condiciones |
|------------|-------------|
| CREADA → CONFIGURACIÓN | Sin condiciones previas |
| CONFIGURACIÓN → EN COMPETICIÓN | Mínimo 2 equipos, cada equipo con entrenador y delegado |
| EN COMPETICIÓN → FINALIZADA | Todos los partidos en estado FINALIZADO |

**Restricciones durante EN COMPETICIÓN:**
- No se pueden añadir equipos
- No se pueden eliminar equipos
- No se pueden modificar reglas/configuración
- No se pueden cambiar roles asignados

### Implementación Actual (`backend/app/models/liga.py`)

```python
class Liga(Base):
    activa = Column(Boolean, nullable=False, default=True)
```

Solo existe un campo booleano `activa`. No hay estados ni transiciones.

### Discrepancias

| # | Regla Documentada | Estado en Backend |
|---|------------------|-------------------|
| 1 | Estados: CREADA, CONFIGURACIÓN, EN COMPETICIÓN, FINALIZADA | ❌ No implementado |
| 2 | Transición CONFIGURACIÓN → EN COMPETICIÓN requiere 2+ equipos | ❌ No implementado |
| 3 | Transición requiere equipos con entrenador y delegado | ❌ No implementado |
| 4 | Transición a FINALIZADA requiere todos partidos finalizados | ❌ No implementado |
| 5 | Prohibición de añadir equipos durante competición | ❌ No implementado |
| 6 | Prohibición de modificar roles durante competición | ❌ No implementado |

**Archivo afectado:** `backend/app/models/liga.py`, `backend/app/api/services/liga_service.py`

---

## 2. Asignación Automática de Roles

### Documentación (`doc/reglas-y-convenciones/usuarios-roles-y-control-de-acceso.md`)

> La asignación de roles se realiza automáticamente según la participación del usuario:

- El **creador de una liga** obtiene automáticamente el rol de **Administrador**
- Al asignar un **entrenador** a un equipo, el usuario obtiene el rol de **Entrenador** en esa liga
- Al asignar un **delegado de campo**, el usuario obtiene el rol de **Delegado de campo**
- Al añadir un **jugador** al equipo, el usuario obtiene el rol de **Jugador**

### Implementación Actual

#### Creación de Liga (`backend/app/api/services/liga_service.py:18-42`)

```python
def crear_liga(db: Session, datos: LigaCreate):
    liga = Liga(nombre=datos.nombre, temporada=datos.temporada)
    db.add(liga)
    db.flush()
    # NO asigna rol de administrador al creador
    configuracion = LigaConfiguracion(id_liga=liga.id_liga)
    db.add(configuracion)
    db.commit()
    return liga
```

#### Creación de Equipo (`backend/app/api/services/equipo_service.py:11-33`)

```python
def crear_equipo(db: Session, datos: EquipoCreate):
    equipo = Equipo(
        nombre=datos.nombre,
        id_entrenador=datos.id_entrenador,
        id_delegado=datos.id_delegado
        # NO asigna roles a entrenador ni delegado
    )
```

#### Creación de Jugador (`backend/app/api/services/jugador_service.py:11-32`)

```python
def crear_jugador(db: Session, datos: JugadorCreate):
    jugador = Jugador(
        id_usuario=datos.id_usuario,
        id_equipo=datos.id_equipo
        # NO asigna rol de jugador
    )
```

### Discrepancias

| # | Regla Documentada | Estado en Backend |
|---|------------------|-------------------|
| 1 | Creador de liga → Rol Administrador | ❌ No implementado |
| 2 | Asignar entrenador → Rol Entrenador | ❌ No implementado |
| 3 | Asignar delegado → Rol Delegado | ❌ No implementado |
| 4 | Añadir jugador → Rol Jugador | ❌ No implementado |

**Archivos afectados:** `liga_service.py`, `equipo_service.py`, `jugador_service.py`

---

## 3. Restricciones de Unicidad

### Documentación (`doc/reglas-y-convenciones/equipos-y-jugadores.md`)

> Para garantizar coherencia y evitar conflictos de gestión:

- Un usuario **no puede ser entrenador de dos equipos distintos dentro de la misma liga**
- Un jugador **no puede pertenecer a más de un equipo dentro de la misma liga**
- Un usuario puede tener roles distintos en ligas diferentes, pero **no roles incompatibles dentro de la misma liga**

### Implementación Actual

No existe ninguna validación en los servicios correspondientes:

- `equipo_service.py`: No valida si el entrenador ya está asignado a otro equipo
- `jugador_service.py`: No valida si el jugador ya pertenece a otro equipo de la misma liga

### Discrepancias

| # | Regla Documentada | Estado en Backend |
|---|------------------|-------------------|
| 1 | Entrenador único por liga | ❌ No implementado |
| 2 | Jugador único por liga | ❌ No implementado |
| 3 | Roles incompatibles en misma liga | ❌ No implementado |

**Archivos afectados:** `backend/app/api/services/equipo_service.py`, `backend/app/api/services/jugador_service.py`

---

## 4. Validaciones de Eventos de Partido

### Documentación (`doc/reglas-y-convenciones/partidos-y-eventos.md`)

| Regla | Descripción |
|-------|-------------|
| E1 | Solo el **delegado de campo** puede registrar eventos |
| E2 | Solo el delegado del **equipo LOCAL** puede crear eventos |
| E3 | No se permite registrar eventos si el partido **no está EN CURSO** |
| E4 | Todo evento debe estar asociado a un **jugador convocado** |
| E5 | Jugador expulsado (tarjeta roja) no puede recibir eventos posteriores |
| E6 | MVP solo puede asignarse **una vez por partido** |

### Implementación Actual (`backend/app/api/services/evento_service.py`)

```python
def crear_evento(db: Session, datos: EventoPartidoCreate, usuario_id: int):
    # Verificar que el usuario tiene el rol de delegate
    usuario_rol = db.query(UsuarioRol).filter(
        UsuarioRol.id_usuario == usuario_id,
        UsuarioRol.id_rol == 5  # Hardcoded
    ).first()

    # Verificar que es delegado del equipo LOCAL
    if equipo_local.id_delegado != usuario_id:
        raise ValueError("Solo el delegado del equipo local...")

    # Crear el evento SIN más validaciones
    evento = EventoPartido(...)
```

### Discrepancias

| # | Regla | Estado en Backend |
|---|-------|-------------------|
| E1 | Solo delegado puede registrar | ✅ Implementado |
| E2 | Solo delegado del equipo LOCAL | ✅ Implementado |
| E3 | Partido debe estar EN CURSO | ❌ No implementado |
| E4 | Jugador debe estar convocado | ❌ No implementado |
| E5 | Jugador expulsado sin eventos posteriores | ❌ No implementado |
| E6 | MVP único por partido | ❌ No implementado |

**Archivos afectados:** `backend/app/api/services/evento_service.py`

---

## 5. Validaciones de Partidos

### Documentación

| Regla | Descripción |
|-------|-------------|
| P1 | Partido debe pertenecer a una liga |
| P2 | Dos equipos distintos |
| P3 | Ambos equipos de la misma liga |
| P4 | Estados: PROGRAMADO → EN CURSO → FINALIZADO |
| P5 | No modificar equipos/participantes si EN CURSO o FINALIZADO |
| P6 | No modificar fecha/hora si EN CURSO o FINALIZADO |

### Implementación Actual (`backend/app/api/services/partido_service.py`)

```python
def crear_partido(db: Session, datos: PartidoCreate):
    partido = Partido(
        id_liga=datos.id_liga,
        id_equipo_local=datos.id_equipo_local,
        id_equipo_visitante=datos.id_equipo_visitante,
        fecha=datos.fecha,
        estado=datos.estado
        # SIN validaciones
    )
```

### Discrepancias

| # | Regla | Estado en Backend |
|---|-------|-------------------|
| P1 | Partido pertenece a liga | ✅ Por foreign key |
| P2 | Equipos distintos | ❌ No validado |
| P3 | Equipos de misma liga | ❌ No validado |
| P4 | Transiciones de estado válidas | ❌ No implementado |
| P5 | Restricción de modificación por estado | ❌ No implementado |
| P6 | Restricción de fecha por estado | ❌ No implementado |

**Archivos afectados:** `backend/app/api/services/partido_service.py`

---

## 6. Eliminación de Entidades

### Documentación

| Entidad | Restricción |
|---------|-------------|
| Liga | Solo si no tiene partidos o todos eliminados |
| Liga en competición | No puede eliminarse |
| Equipo | No permitido si tiene partidos programados o jugados |

### Implementación Actual

```python
# liga_service.py
def eliminar_liga(db: Session, liga_id: int):
    liga = obtener_liga_por_id(db, liga_id)
    if not liga:
        raise ValueError("Liga no encontrada")
    db.delete(liga)
    db.commit()
    # SIN validaciones de partidos existentes

# equipo_service.py
def eliminar_equipo(db: Session, equipo_id: int):
    equipo = obtener_equipo_por_id(db, equipo_id)
    if not equipo:
        raise ValueError("Equipo no encontrado")
    db.delete(equipo)
    db.commit()
    # SIN validaciones de partidos existentes
```

### Discrepancias

| # | Regla | Estado en Backend |
|---|-------|-------------------|
| 1 | No eliminar liga con partidos | ❌ No implementado |
| 2 | No eliminar liga en competición | ❌ No implementado |
| 3 | No eliminar equipo con partidos | ❌ No implementado |

**Archivos afectados:** `liga_service.py`, `equipo_service.py`

---

## 7. Permisos y Control de Acceso

### Documentación (`doc/roles-y-permisos/matriz-de-permisos.md`)

| Rol | Permisos |
|-----|----------|
| Admin | Gestión completa de liga, equipos, usuarios |
| Coach | Gestión de su equipo, alineaciones, convocatorias |
| Delegate | Registro de eventos del partido |
| Player | Ver su equipo y estadísticas personales |
| Viewer | Ver información pública |

### Implementación Actual

✅ Los permisos básicos RBAC están implementados correctamente en `dependencies.py`:

```python
def require_role(role_name: str):
    def dependency(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
        # Verifica que el usuario tiene el rol requerido
```

### Discrepancias

| # | Aspecto | Estado |
|---|---------|--------|
| 1 | Permisos básicos por rol | ✅ Implementado |
| 2 | Permisos por liga específica | ❌ No implementado (roles globales) |
| 3 | Coach solo gestiona SU equipo | ❌ No implementado |
| 4 | Delegate solo eventos de SU partido | ⚠️ Parcial (solo local) |

---

## 8. Detalle de Archivos que Requieren Modificación

| Archivo | Cambios Necesarios |
|---------|-------------------|
| `models/liga.py` | Añadir campo `estado` con valores: CREADA, CONFIGURACION, EN_COMPETICION, FINALIZADA |
| `services/liga_service.py` | Validar transiciones de estado, asignar rol admin al creador |
| `services/equipo_service.py` | Asignar roles, validar unicidad de entrenador, validar eliminación |
| `services/jugador_service.py` | Asignar rol, validar unicidad por liga |
| `services/evento_service.py` | Validar estado del partido, convocatoria, expulsión, MVP único |
| `services/partido_service.py` | Validar equipos de misma liga, transiciones de estado |
| `models/evento_partido.py` | Posiblemente añadir validaciones |
| `schemas/partido.py` | Añadir validaciones en schemas |

---

## 9. Recomendaciones

### Prioridad Alta (Crítico)

1. **Implementar estados de liga** con transiciones válidas
2. **Asignación automática de roles** al crear/participar en entidades
3. **Validar partidos**: equipos de misma liga, equipos distintos
4. **Validar eliminación**: no permitir si hay entidades relacionadas

### Prioridad Media (Importante)

5. **Validaciones de eventos**: partido en curso, jugador convocado, MVP único
6. **Restricciones de unicidad**: entrenador/jugador único por liga
7. **Permisos por liga**: roles específicos por competición

### Prioridad Baja (Mejora)

8. **Validación de jugador expulsado** sin eventos posteriores
9. **Logs de auditoría** para cambios de estado
10. **Notificaciones** automáticas por cambios de estado

---

## 10. Conclusión

El análisis revela una **brecha significativa** entre la documentación y la implementación actual. Mientras que la documentación describe un sistema robusto con:

- Ciclo de vida de entidades
- Asignación automática de roles
- Validaciones de integridad
- Restricciones por estado

La implementación actual es **mucho más permisiva** y permite:

- Crear partidos con equipos de diferentes ligas
- Eliminar ligas/equipos con partidos asociados
- Crear eventos sin validar estado del partido
- Asignar roles manualmente sin automatización

**Se recomienda priorizar la implementación de las reglas de negocio documentadas para garantizar la integridad del sistema.**

---

*Informe generado automáticamente a partir del análisis del código fuente y documentación.*