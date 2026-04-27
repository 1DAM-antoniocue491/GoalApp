# Plan de Implementación: Notificaciones

## 1. Estado Actual

### Archivos existentes

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `src/app/notifications/index.tsx` | **Vacío** | Archivo existe pero sin contenido |
| `src/features/notifications/components/*.tsx` | UI Only | Componentes visuales (NotificationCard, NotificationFilterTabs, NotificationsScreen) |
| `src/features/notifications/api/notifications.api.ts` | **Vacío** | Sin implementación |
| `src/features/notifications/hooks/useNotifications.ts` | **Vacío** | Sin implementación |
| `src/features/notifications/services/notificationsService.ts` | **Vacío** | Sin implementación |
| `src/features/notifications/types/notifications.types.ts` | **Vacío** | Sin tipos |

### Datos actuales

- **Notificaciones**: Sin implementación. La pantalla está vacía.
- **Filtros**: Componente `NotificationFilterTabs` existe pero sin funcionalidad
- **Badge de notificaciones**: El dashboard muestra `notificationCount` pero sin datos reales

### Qué falta implementar

1. Implementar API completa de notificaciones
2. Implementar hook con polling para notificaciones no leídas
3. Implementar marcado como leído (individual y todas)
4. Implementar eliminación de notificaciones
5. Conectar pantalla de notificaciones

---

## 2. Endpoints del Backend

| Endpoint | Método | Existe | Datos que devuelve |
|----------|--------|--------|-------------------|
| `GET /notificaciones/` | GET | ✅ | Todas las notificaciones (`NotificacionResponse[]`) |
| `GET /notificaciones/no-leidas` | GET | ✅ | Notificaciones no leídas |
| `POST /notificaciones/` | POST | ✅ | Crear notificación (solo admin) |
| `PATCH /notificaciones/{id}/leer` | PATCH | ✅ | Marcar como leída |
| `PUT /notificaciones/mark-all-read` | PUT | ✅ | Marcar todas como leídas |
| `DELETE /notificaciones/{id}` | DELETE | ✅ | Eliminar notificación |

### Endpoints que faltan en el backend

No faltan endpoints. El backend tiene completa la API de notificaciones.

---

## 3. Estructura de Archivos a Crear/Completar

```
src/features/notifications/
├── api/notifications.api.ts       # COMPLETAR
├── types/notifications.types.ts   # COMPLETAR
├── hooks/useNotifications.ts      # COMPLETAR
├── services/notificationsService.ts # COMPLETAR
└── components/
    ├── NotificationsScreen.tsx    # CONECTAR
    ├── NotificationCard.tsx       # CONECTAR
    └── NotificationFilterTabs.tsx # CONECTAR
```

---

## 4. Código de Ejemplo

### 4.1 Tipos (`types/notifications.types.ts`)

```typescript
/**
 * Tipos para notificaciones
 * Basados en app/schemas/notificacion.py
 */

export type NotificationType =
  | 'partido_finalizado'
  | 'convocatoria'
  | 'recordatorio'
  | 'mensaje'
  | 'sistema';

export interface NotificacionResponse {
  id_notificacion: number;
  id_usuario: number;
  tipo: NotificationType | string;
  titulo: string;
  mensaje: string;
  leida: boolean;
  id_referencia: number | null;
  tipo_referencia: string | null; // 'partido', 'liga', 'equipo'
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

export interface NotificacionCreate {
  id_usuario: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  leida?: boolean;
  id_referencia?: number | null;
  tipo_referencia?: string | null;
}
```

> **💡 Por qué este archivo:**
> - `NotificationType` como union type da autocompletado y evita errores al filtrar por tipo
> - `id_referencia` y `tipo_referencia` permiten navegar al recurso relacionado (partido/liga/equipo)
> - `leida: boolean` es el estado que controla si la notificación aparece como leída en la UI
> - **Sin esto:** No sabrías qué tipos de notificaciones existen ni cómo navegar a su referencia
>
> **💡 Consejo:**
> - `| string` en `tipo` permite manejar tipos nuevos del backend sin romper el código
> - `NotificacionCreate` es para crear notificaciones (solo admin), los campos opcionales permiten flexibilidad

### 4.2 Capa API (`api/notifications.api.ts`)

```typescript
import { apiClient } from '@/src/shared/api/client';
import type {
  NotificacionResponse,
  NotificacionCreate,
} from '../types/notifications.types';

/**
 * GET /notificaciones/ - Todas las notificaciones
 */
export async function getNotifications(): Promise<NotificacionResponse[]> {
  const response = await apiClient.get<NotificacionResponse[]>('/notificaciones/');
  return response.data;
}

/**
 * GET /notificaciones/no-leidas - Notificaciones no leídas
 */
export async function getUnreadNotifications(): Promise<NotificacionResponse[]> {
  const response = await apiClient.get<NotificacionResponse[]>(
    '/notificaciones/no-leidas'
  );
  return response.data;
}

/**
 * PATCH /notificaciones/{id}/leer - Marcar como leída
 */
export async function markAsRead(notificationId: number): Promise<void> {
  await apiClient.patch(`/notificaciones/${notificationId}/leer`);
}

/**
 * PUT /notificaciones/mark-all-read - Marcar todas como leídas
 */
export async function markAllAsRead(): Promise<{ mensaje: string; cantidad: number }> {
  const response = await apiClient.put<{ mensaje: string; cantidad: number }>(
    '/notificaciones/mark-all-read'
  );
  return response.data;
}

/**
 * DELETE /notificaciones/{id} - Eliminar notificación
 */
export async function deleteNotification(notificationId: number): Promise<void> {
  await apiClient.delete(`/notificaciones/${notificationId}`);
}

/**
 * POST /notificaciones/ - Crear notificación (solo admin)
 */
export async function createNotification(
  data: NotificacionCreate
): Promise<NotificacionResponse> {
  const response = await apiClient.post<NotificacionResponse>(
    '/notificaciones/',
    data
  );
  return response.data;
}
```

> **💡 Por qué esta capa:**
> - Cada acción de notificación tiene su función: leer, marcar todas, eliminar, crear
> - `markAsRead` devuelve `void` porque el backend no devuelve body, solo 204 No Content
> - `markAllAsRead` devuelve `{ mensaje, cantidad }` para mostrar feedback al usuario ("5 marcadas como leídas")
> - **Sin esto:** Tendrías que recordar qué endpoint usa PATCH vs PUT vs DELETE manualmente
>
> **💡 Consejo:**
> - `getUnreadNotifications` es útil para el badge del dashboard sin cargar todas las notificaciones
> - El tipado `<{ mensaje: string; cantidad: number }>` en `markAllAsRead` documenta qué devuelve el backend

### 4.3 Service (`services/notificationsService.ts`)

```typescript
import {
  getNotifications,
  getUnreadNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
} from '../api/notifications.api';
import type { NotificacionResponse } from '../types/notifications.types';

/**
 * Formatea tiempo relativo para notificación
 */
export function formatNotificationTime(fecha: string): string {
  const date = new Date(fecha);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Ahora';
  if (diffMins < 60) return `hace ${diffMins} min`;
  if (diffHours < 24) return `hace ${diffHours} h`;
  if (diffDays < 7) return `hace ${diffDays} d`;
  return date.toLocaleDateString('es-ES');
}

/**
 * Obtiene todas las notificaciones
 */
export async function fetchNotifications(): Promise<NotificacionResponse[]> {
  return getNotifications();
}

/**
 * Obtiene notificaciones no leídas
 */
export async function fetchUnreadNotifications(): Promise<NotificacionResponse[]> {
  return getUnreadNotifications();
}

/**
 * Marca notificación como leída
 */
export async function markNotificationAsRead(notificationId: number): Promise<void> {
  return markAsRead(notificationId);
}

/**
 * Marca todas como leídas
 */
export async function markAllNotificationsAsRead(): Promise<{ mensaje: string; cantidad: number }> {
  return markAllAsRead();
}

/**
 * Elimina notificación
 */
export async function removeNotification(notificationId: number): Promise<void> {
  return deleteNotification(notificationId);
}
```

> **💡 Por qué esta capa:**
> - `formatNotificationTime` centraliza el formato de tiempo relativo ("hace 5 min", "hace 2 h")
> - La lógica de cálculo de tiempo está en un solo lugar, consistente en toda la app
> - Las funciones `fetch*` y `mark*` son wrappers que pueden añadir logging o caché después
> - **Sin esto:** Cada componente calcularía el tiempo relativo diferente, inconsistente para el usuario
>
> **💡 Consejo:**
> - `diffMins < 1` muestra "Ahora" para notificaciones muy recientes, mejor UX que "hace 0 min"
> - Después de 7 días muestra la fecha completa, útil para notificaciones antiguas

### 4.4 Hook (`hooks/useNotifications.ts`)

```typescript
import { useState, useEffect, useCallback } from 'react';
import {
  fetchNotifications,
  fetchUnreadNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  removeNotification,
} from '../services/notificationsService';
import type { NotificacionResponse } from '../types/notifications.types';

interface UseNotificationsResult {
  notifications: NotificacionResponse[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  delete: (id: number) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useNotifications(refreshInterval = 30000): UseNotificationsResult {
  const [notifications, setNotifications] = useState<NotificacionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchNotifications();
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar notificaciones');
    } finally {
      setLoading(false);
    }
  }, []);

  const markAsRead = async (id: number) => {
    try {
      await markNotificationAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id_notificacion === id ? { ...n, leida: true } : n))
      );
    } catch (err) {
      console.error('Error al marcar como leída:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, leida: true })));
    } catch (err) {
      console.error('Error al marcar todas como leídas:', err);
    }
  };

  const deleteNotification = async (id: number) => {
    try {
      await removeNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id_notificacion !== id));
    } catch (err) {
      console.error('Error al eliminar:', err);
    }
  };

  useEffect(() => {
    loadData();

    // Polling para notificaciones no leídas
    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);
  }, [loadData, refreshInterval]);

  const unreadCount = notifications.filter((n) => !n.leida).length;

  return {
    notifications,
    unreadCount,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    delete: deleteNotification,
    refresh: loadData,
  };
}
```

> **💡 Por qué este hook:**
> - `useCallback` en `loadData` memoiza la función, evita recrearla en cada render
> - Polling cada 30 segundos (`refreshInterval = 30000`) mantiene las notificaciones actualizadas
> - `markAsRead` y `delete` actualizan el estado local inmediatamente, la UI responde sin esperar recarga
> - **Sin esto:** El usuario tendría que recargar manualmente para ver notificaciones nuevas
>
> **💡 Consejo:**
> - `unreadCount` se calcula en cada render, útil para el badge del dashboard
> - El cleanup `return () => clearInterval(interval)` evita memory leaks cuando el componente se desmonta

---

## 5. Orden de Implementación

| Paso | Acción | Archivos | Tiempo estimado |
|------|--------|----------|-----------------|
| 1 | Crear tipos | `types/notifications.types.ts` | ~15 min |
| 2 | Crear capa API | `api/notifications.api.ts` | ~25 min |
| 3 | Crear service | `services/notificationsService.ts` | ~20 min |
| 4 | Crear hook | `hooks/useNotifications.ts` | ~30 min |
| 5 | Implementar NotificationsScreen | `components/NotificationsScreen.tsx` | ~45 min |
| 6 | Conectar NotificationCard | `components/NotificationCard.tsx` | ~20 min |
| 7 | Integrar badge en dashboard | `features/dashboard/components/*.tsx` | ~20 min |

**Total estimado: ~3 horas**

---

## 6. Notas Adicionales

- **Polling**: El hook incluye polling cada 30 segundos para notificaciones no leídas. Ajustar según necesidades.
- **Tipos de notificación**: El backend usa strings para `tipo`. El frontend puede querer mapear a iconos/colors según tipo.
- **Referencias**: Las notificaciones pueden tener `id_referencia` y `tipo_referencia` para navegar al partido/liga/equipo relacionado.
- **Badge count**: El `notificationCount` en `activeLeagueStore` debe actualizarse con `unreadCount` del hook.
