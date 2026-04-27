# Plan de Implementación: Perfil

## 1. Estado Actual

### Archivos existentes

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `src/app/(tabs)/profile.tsx` | Parcial | Usa `useAuth` para usuario, pero datos hardcodeados |
| `src/app/profile/editProfile.tsx` | UI Only | Formulario de edición con datos hardcodeados |
| `src/features/profile/components/*.tsx` | UI Only | Componentes visuales (ProfileMenu, EditProfileModal, etc.) |
| `src/features/profile/api/profile.api.ts` | **Vacío** | Sin implementación |
| `src/features/profile/hooks/useProfile.ts` | **Vacío** | Sin implementación |
| `src/features/profile/services/profileService.ts` | **Vacío** | Sin implementación |
| `src/features/profile/types/profile.types.ts` | **Vacío** | Sin tipos |

### Datos actuales

- **Nombre**: "Pepe Luis" hardcodeado (fallback), usa `user?.nombre` de auth
- **Email**: "john.doe@goalapp.com" hardcodeado (fallback)
- **Teléfono**: "+34 790 67 84 35" hardcodeado
- **Fecha nacimiento**: "15 de junio, 2005" hardcodeado
- **Género**: "Masculino" hardcodeado
- **Rol**: "Administrador" hardcodeado

### Qué falta implementar

1. Conectar API para obtener perfil completo (`GET /usuarios/me`)
2. Conectar API para actualizar perfil (`PUT /usuarios/{usuario_id}`)
3. Implementar subida de imagen de perfil (si existe endpoint)
4. Conectar formulario de edición a datos reales

---

## 2. Endpoints del Backend

| Endpoint | Método | Existe | Datos que devuelve |
|----------|--------|--------|-------------------|
| `GET /usuarios/me` | GET | ✅ | Usuario actual (`UsuarioResponse`) |
| `GET /usuarios/{usuario_id}` | GET | ✅ | Usuario por ID |
| `PUT /usuarios/{usuario_id}` | PUT | ✅ | Usuario actualizado |
| `GET /usuarios/me/ligas` | GET | ✅ | Ligas con rol del usuario |
| `GET /usuarios/me/ligas-seguidas` | GET | ✅ | Ligas seguidas |

### Endpoints que faltan en el backend

No faltan endpoints. El backend tiene completa la API de perfil de usuario.

---

## 3. Estructura de Archivos a Crear/Completar

```
src/features/profile/
├── api/profile.api.ts          # COMPLETAR
├── types/profile.types.ts      # COMPLETAR
├── hooks/useProfile.ts         # COMPLETAR
└── services/profileService.ts  # COMPLETAR
```

---

## 4. Código de Ejemplo

### 4.1 Tipos (`types/profile.types.ts`)

```typescript
/**
 * Tipos para perfil de usuario
 * Basados en app/schemas/usuario.py
 */

export type GeneroEnum = 'masculino' | 'femenino' | 'otro';

export interface UsuarioResponse {
  id_usuario: number;
  nombre: string;
  email: string;
  genero: GeneroEnum | null;
  telefono: string | null;
  fecha_nacimiento: string | null; // ISO 8601 (YYYY-MM-DD)
  imagen_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface UsuarioUpdate {
  nombre?: string | null;
  email?: string | null;
  contraseña?: string | null;
  genero?: GeneroEnum | null;
  telefono?: string | null;
  fecha_nacimiento?: string | null;
  imagen_url?: string | null;
}

export interface LigaConRolResponse {
  id_liga: number;
  nombre: string;
  temporada: string;
  activa: boolean;
  rol: string;
  equipos_total: number;
}
```

> **💡 Por qué este archivo:**
> - `GeneroEnum` como union type da autocompletado y evita errores de escritura
> - `UsuarioResponse` tiene campos obligatorios (`nombre`, `email`) y opcionales (`| null`) según el backend
> - `UsuarioUpdate` usa todos los campos opcionales (`?`) porque el PATCH solo actualiza lo enviado
> - **Sin esto:** Podrías enviar campos undefined al backend o no manejar casos null en la UI
>
> **💡 Consejo:**
> - `fecha_nacimiento: string` es ISO 8601 (`YYYY-MM-DD`), fácil de parsear con `new Date()`
> - El comentario `/** Basados en app/schemas/usuario.py */` documenta el origen de los tipos

### 4.2 Capa API (`api/profile.api.ts`)

```typescript
import { apiClient } from '@/src/shared/api/client';
import type {
  UsuarioResponse,
  UsuarioUpdate,
  LigaConRolResponse,
} from '../types/profile.types';

/**
 * GET /usuarios/me - Obtener perfil del usuario actual
 */
export async function getCurrentUserProfile(): Promise<UsuarioResponse> {
  const response = await apiClient.get<UsuarioResponse>('/usuarios/me');
  return response.data;
}

/**
 * PUT /usuarios/{usuarioId} - Actualizar perfil
 */
export async function updateUserProfile(
  usuarioId: number,
  data: UsuarioUpdate
): Promise<UsuarioResponse> {
  const response = await apiClient.put<UsuarioResponse>(
    `/usuarios/${usuarioId}`,
    data
  );
  return response.data;
}

/**
 * GET /usuarios/me/ligas - Obtener ligas donde el usuario tiene rol
 */
export async function getUserLeaguesWithRole(): Promise<LigaConRolResponse[]> {
  const response = await apiClient.get<LigaConRolResponse[]>(
    '/usuarios/me/ligas'
  );
  return response.data;
}

/**
 * GET /usuarios/me/ligas-seguidas - Obtener ligas seguidas
 */
export async function getUserFollowedLeagues(): Promise<LigaConRolResponse[]> {
  const response = await apiClient.get<LigaConRolResponse[]>(
    '/usuarios/me/ligas-seguidas'
  );
  return response.data;
}
```

> **💡 Por qué esta capa:**
> - `/usuarios/me` es el endpoint estándar para obtener el perfil del usuario autenticado
> - `updateUserProfile` recibe `UsuarioUpdate` que tiene todos los campos opcionales, envía solo lo necesario
> - Las funciones para ligas (`getUserLeaguesWithRole`, `getUserFollowedLeagues`) están separadas porque son casos de uso distintos
> - **Sin esto:** Tendrías que construir las URLs y el body del PUT manualmente en cada lugar
>
> **💡 Consejo:**
> - El tipado `<UsuarioResponse>` en `apiClient.put` asegura que la respuesta tenga la estructura esperada
> - `UsuarioUpdate` permite enviar solo `{ nombre: 'nuevo' }` sin tener que incluir todos los campos

### 4.3 Service (`services/profileService.ts`)

```typescript
import {
  getCurrentUserProfile,
  updateUserProfile,
  getUserLeaguesWithRole,
  getUserFollowedLeagues,
} from '../api/profile.api';
import type {
  UsuarioResponse,
  UsuarioUpdate,
  LigaConRolResponse,
} from '../types/profile.types';

/**
 * Formatea fecha de nacimiento para mostrar en UI
 */
export function formatBirthDate(fecha: string | null): string {
  if (!fecha) return 'No especificada';
  const date = new Date(fecha);
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Formatea género para mostrar en UI
 */
export function formatGender(genero: GeneroEnum | null): string {
  if (!genero) return 'No especificado';
  const labels: Record<GeneroEnum, string> = {
    masculino: 'Masculino',
    femenino: 'Femenino',
    otro: 'Otro',
  };
  return labels[genero];
}

/**
 * Obtiene perfil completo del usuario
 */
export async function fetchUserProfile(): Promise<UsuarioResponse> {
  return getCurrentUserProfile();
}

/**
 * Actualiza perfil del usuario
 */
export async function updateProfile(
  usuarioId: number,
  data: UsuarioUpdate
): Promise<UsuarioResponse> {
  return updateUserProfile(usuarioId, data);
}

/**
 * Obtiene ligas del usuario con roles
 */
export async function fetchUserLeaguesWithRole(): Promise<LigaConRolResponse[]> {
  return getUserLeaguesWithRole();
}
```

> **💡 Por qué esta capa:**
> - `formatBirthDate` y `formatGender` centralizan el formateo, consistente en toda la app
> - Las funciones de formateo manejan casos `null` gracefulmente ("No especificada" en vez de crash)
> - Esta capa puede añadir validación antes de actualizar (ej: verificar contraseña) sin tocar la API
> - **Sin esto:** Cada componente formatearía fechas y géneros diferente, inconsistente para el usuario
>
> **💡 Consejo:**
> - `Record<GeneroEnum, string>` es un objeto mapeado tipado, TypeScript te avisa si falta un género
> - Las funciones `fetch*` y `update*` son wrappers que pueden crecer después (validación, logging)

### 4.4 Hook (`hooks/useProfile.ts`)

```typescript
import { useState, useEffect } from 'react';
import {
  fetchUserProfile,
  updateProfile,
  fetchUserLeaguesWithRole,
} from '../services/profileService';
import type {
  UsuarioResponse,
  UsuarioUpdate,
  LigaConRolResponse,
} from '../types/profile.types';

interface UseProfileResult {
  profile: UsuarioResponse | null;
  leaguesWithRole: LigaConRolResponse[];
  loading: boolean;
  error: string | null;
  update: (data: UsuarioUpdate) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useProfile(): UseProfileResult {
  const [profile, setProfile] = useState<UsuarioResponse | null>(null);
  const [leaguesWithRole, setLeaguesWithRole] = useState<LigaConRolResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [profileData, leaguesData] = await Promise.all([
        fetchUserProfile(),
        fetchUserLeaguesWithRole(),
      ]);

      setProfile(profileData);
      setLeaguesWithRole(leaguesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar perfil');
    } finally {
      setLoading(false);
    }
  };

  const update = async (data: UsuarioUpdate) => {
    if (!profile) throw new Error('No hay perfil cargado');
    try {
      const updated = await updateProfile(profile.id_usuario, data);
      setProfile(updated);
    } catch (err) {
      throw err;
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return {
    profile,
    leaguesWithRole,
    loading,
    error,
    update,
    refresh: loadData,
  };
}
```

> **💡 Por qué este hook:**
> - Carga perfil y ligas en paralelo con `Promise.all`, más rápido que secuencial
> - La función `update` actualiza el estado local tras guardar, la UI refleja el cambio inmediatamente
> - `refresh` permite recargar datos si otro componente modificó el perfil
> - **Sin esto:** Cada pantalla de perfil repetiría la lógica de carga, actualización y manejo de errores
>
> **💡 Consejo:**
> - El array vacío `[]` en `useEffect` significa "solo al montar", el perfil no se recarga solo
> - `if (!profile) throw new Error` protege contra llamadas a `update` antes de cargar los datos

---

## 5. Orden de Implementación

| Paso | Acción | Archivos | Tiempo estimado |
|------|--------|----------|-----------------|
| 1 | Crear tipos | `types/profile.types.ts` | ~15 min |
| 2 | Crear capa API | `api/profile.api.ts` | ~20 min |
| 3 | Crear service | `services/profileService.ts` | ~20 min |
| 4 | Crear hook | `hooks/useProfile.ts` | ~25 min |
| 5 | Conectar profile.tsx | `app/(tabs)/profile.tsx` | ~30 min |
| 6 | Conectar editProfile.tsx | `app/profile/editProfile.tsx` | ~45 min |

**Total estimado: ~2.5 horas**

---

## 6. Notas Adicionales

- **Auth existente**: El hook `useAuth` ya proporciona `user?.nombre` y `user?.email`. El hook `useProfile` debe complementar con datos adicionales (teléfono, fecha_nacimiento, género).
- **Contraseña**: El backend permite actualizar contraseña con campo `contraseña`. El frontend debe tener validación de seguridad (mínimo 6 caracteres, confirmación).
- **Imagen de perfil**: El backend tiene campo `imagen_url`. Si hay subida de imágenes, necesitaría endpoint específico en `imagenes.py`.
