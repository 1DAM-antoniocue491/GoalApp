# Plan de Implementación: Liga

## 1. Estado Actual

### Archivos existentes

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `src/app/(tabs)/index.tsx` | UI Only | Pantalla principal de Liga, delega a componentes |
| `src/app/league/classification.tsx` | UI Only | Tabla de clasificación con datos hardcodeados |
| `src/app/league/match.tsx` | UI Only | Componente que renderiza tabs de partidos |
| `src/app/league/teams.tsx` | UI Only | Lista de equipos con datos hardcodeados |
| `src/app/league/teams/team.tsx` | UI Only | Detalle de equipo (hardcodeado) |
| `src/app/league/teams/information.tsx` | UI Only | Información del equipo |
| `src/app/league/teams/squad.tsx` | UI Only | Plantilla del equipo |
| `src/app/league/users.tsx` | UI Only | Usuarios de la liga |
| `src/features/leagues/components/*.tsx` | UI Only | Componentes visuales (LeagueCard, LeagueTabs, etc.) |
| `src/features/leagues/api/leagues.api.ts` | **Vacío** | Archivo creado pero sin implementación |
| `src/features/leagues/hooks/useLeagues.ts` | **Vacío** | Hook sin implementación |
| `src/features/leagues/services/leagueService.ts` | Mock | Solo usa datos mockeados |
| `src/features/leagues/types/league.api.types.ts` | **Vacío** | Tipos sin definir |

### Datos actuales

- **Liga**: Datos hardcodeados en `leagueService.ts` usando `mockLeagues`
- **Clasificación**: Datos estáticos en `classification.tsx` (todos en 0)
- **Equipos**: Imágenes locales hardcodeadas (`betis.png`, `realMadrid.png`)
- **Usuarios**: Sin implementación

### Qué falta implementar

1. Conectar `useLeagues` hook al backend para obtener ligas reales
2. Implementar endpoint de clasificación (`GET /ligas/{liga_id}/clasificacion`)
3. Implementar endpoint de equipos de liga
4. Implementar endpoint de usuarios de liga
5. Conectar componentes UI a datos reales

---

## 2. Endpoints del Backend

| Endpoint | Método | Existe | Datos que devuelve |
|----------|--------|--------|-------------------|
| `GET /ligas/` | GET | ✅ | Lista de todas las ligas (`LigaResponse[]`) |
| `GET /ligas/{liga_id}` | GET | ✅ | Detalle de liga (`LigaResponse`) |
| `GET /ligas/{liga_id}/clasificacion` | GET | ✅ | Tabla de clasificación (`ClasificacionItem[]`) |
| `GET /ligas/{liga_id}/usuarios` | GET | ✅ | Usuarios con roles (`UsuarioLigaResponse[]`) |
| `GET /equipos/` | GET | ✅ | Lista de equipos (`EquipoResponse[]`) |
| `GET /equipos/?liga_id={id}` | GET | ✅ | Equipos filtrados por liga |

### Endpoints que faltan en el backend

No faltan endpoints principales.

---

## 3. Estructura de Archivos a Crear/Completar

```
src/features/leagues/
├── api/leagues.api.ts          # COMPLETAR
├── types/league.api.types.ts   # COMPLETAR
├── hooks/useLeagues.ts         # COMPLETAR
└── services/leagueService.ts   # MODIFICAR

src/features/teams/
├── api/teams.api.ts            # COMPLETAR
├── types/teams.types.ts        # COMPLETAR
└── hooks/useTeams.ts           # COMPLETAR
```

---

## 4. Código de Ejemplo

### 4.1 Tipos (`types/league.api.types.ts`)

```typescript
export interface LigaResponse {
  id_liga: number;
  nombre: string;
  temporada: string;
  categoria: string | null;
  activa: boolean;
  cantidad_partidos: number | null;
  duracion_partido: number | null;
  logo_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClasificacionItem {
  posicion: number;
  id_equipo: number;
  nombre_equipo: string;
  puntos: number;
  partidos_jugados: number;
  victorias: number;
  empates: number;
  derrotas: number;
  goles_favor: number;
  goles_contra: number;
  diferencia_goles: number;
}

export interface UsuarioLigaResponse {
  id_usuario: number;
  nombre: string;
  email: string;
  id_rol: number;
  rol: string;
  activo: boolean;
}

export interface EquipoResponse {
  id_equipo: number;
  nombre: string;
  escudo: string | null;
  colores: string | null;
  id_liga: number;
  id_entrenador: number | null;
  id_delegado: number | null;
  created_at: string;
  updated_at: string;
}
```

> **💡 Por qué este archivo:**
> - Define la estructura exacta que devuelve el backend para ligas, clasificación, usuarios y equipos
> - TypeScript usa estas interfaces para darte autocompletado y validación en tiempo de compilación
> - Los nombres de campos coinciden exactamente con el backend (`id_liga` no `idLiga`) para evitar errores de mapeo
> - **Sin esto:** Tendrías que adivinar qué campos existen hasta que el código falle en runtime
>
> **💡 Consejo:**
> - Si el backend cambia un campo, TypeScript te avisará al compilar en lugar de fallar en producción
> - Usa `| null` para campos opcionales del backend, así evitas `undefined is not an object`

### 4.2 Capa API (`api/leagues.api.ts`)

```typescript
import { apiClient } from '@/src/shared/api/client';
import type {
  LigaResponse,
  ClasificacionItem,
  UsuarioLigaResponse,
  EquipoResponse,
} from '../types/league.api.types';

export async function getLeagues(): Promise<LigaResponse[]> {
  const response = await apiClient.get<LigaResponse[]>('/ligas/');
  return response.data;
}

export async function getLeagueById(ligaId: number): Promise<LigaResponse> {
  const response = await apiClient.get<LigaResponse>(`/ligas/${ligaId}`);
  return response.data;
}

export async function getLeagueClassification(
  ligaId: number
): Promise<ClasificacionItem[]> {
  const response = await apiClient.get<ClasificacionItem[]>(
    `/ligas/${ligaId}/clasificacion`
  );
  return response.data;
}

export async function getLeagueUsers(ligaId: number): Promise<UsuarioLigaResponse[]> {
  const response = await apiClient.get<UsuarioLigaResponse[]>(
    `/ligas/${ligaId}/usuarios`
  );
  return response.data;
}

export async function getTeamsByLeague(ligaId: number): Promise<EquipoResponse[]> {
  const response = await apiClient.get<EquipoResponse[]>(
    `/equipos/?liga_id=${ligaId}`
  );
  return response.data;
}
```

> **💡 Por qué esta capa:**
> - Centraliza todas las llamadas HTTP en un solo archivo, fácil de mantener y testear
> - `apiClient` ya incluye el token JWT, interceptores de error y baseURL configurada
> - Cada función representa un endpoint específico, así sabes exactamente qué URL se llama
> - **Sin esto:** Tendrías llamadas `fetch` dispersas por componentes, duplicando código y sin manejo consistente de errores
>
> **💡 Consejo:**
> - El tipado genérico `<Tipo>` en `apiClient.get<Tipo>()` asegura que la respuesta tenga la estructura esperada
> - Si cambia la URL de un endpoint, solo lo modificas aquí y no en 10 componentes diferentes

### 4.3 Service (`services/leagueService.ts`)

```typescript
import {
  getLeagues,
  getLeagueClassification,
  getLeagueUsers,
  getTeamsByLeague,
} from '../api/leagues.api';
import type { LeagueItem } from '@/src/shared/types/league';

function mapLeagueResponseToLeagueItem(
  league: LigaResponse,
  userRole?: string
): LeagueItem {
  return {
    id: String(league.id_liga),
    name: league.nombre,
    season: league.temporada,
    status: league.activa ? 'active' : 'finished',
    role: (userRole as LeagueRole) || 'player',
    isFavorite: false,
    teamsCount: 0,
    crestUrl: league.logo_url,
  };
}

export async function fetchUserLeagues(): Promise<LeagueItem[]> {
  const leagues = await getLeagues();
  return leagues.map((league) => mapLeagueResponseToLeagueItem(league));
}

export async function fetchClassification(ligaId: number) {
  return getLeagueClassification(ligaId);
}

export async function fetchLeagueUsers(ligaId: number) {
  return getLeagueUsers(ligaId);
}

export async function fetchTeamsByLeague(ligaId: number) {
  return getTeamsByLeague(ligaId);
}
```

> **💡 Por qué esta capa:**
> - Transforma los datos del backend al formato que necesita la UI (ej: `activa` → `'active' | 'finished'`)
> - La función `mapLeagueResponseToLeagueItem` aísla el mapeo, fácil de ajustar si cambia el backend
> - Separa la lógica de negocio de la capa HTTP pura
> - **Sin esto:** Los componentes tendrían que hacer el mapeo manualmente, duplicando lógica en cada lugar
>
> **💡 Consejo:**
> - Los datos crudos del backend rara vez coinciden exactamente con lo que necesita la UI
> - Esta capa es el lugar perfecto para añadir validación o transformación adicional sin ensuciar los componentes

### 4.4 Hook (`hooks/useLeagues.ts`)

```typescript
import { useState, useEffect } from 'react';
import {
  fetchUserLeagues,
  fetchClassification,
  fetchLeagueUsers,
} from '../services/leagueService';
import type { LeagueItem, ClasificacionItem, UsuarioLigaResponse } from '../types/league.api.types';

interface UseLeaguesResult {
  leagues: LeagueItem[];
  classification: ClasificacionItem[];
  users: UsuarioLigaResponse[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useLeagues(ligaId?: number): UseLeaguesResult {
  const [leagues, setLeagues] = useState<LeagueItem[]>([]);
  const [classification, setClassification] = useState<ClasificacionItem[]>([]);
  const [users, setUsers] = useState<UsuarioLigaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const leaguesData = await fetchUserLeagues();
      setLeagues(leaguesData);

      if (ligaId) {
        const [classificationData, usersData] = await Promise.all([
          fetchClassification(ligaId),
          fetchLeagueUsers(ligaId),
        ]);
        setClassification(classificationData);
        setUsers(usersData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar ligas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [ligaId]);

  return {
    leagues,
    classification,
    users,
    loading,
    error,
    refresh: loadData,
  };
}
```

> **💡 Por qué este hook:**
> - Gestiona el estado asíncrono fuera del componente, reutilizable en múltiples pantallas
> - `useEffect` se ejecuta después del render inicial y cuando cambia `ligaId`, asegurando datos actualizados
> - Retorna `loading`, `error`, `data` para que la UI maneje cada estado fácilmente
> - **Sin esto:** Cada componente repetiría la misma lógica de `useState` + `useEffect` + manejo de errores
>
> **💡 Consejo:**
> - El patrón `try/catch/finally` asegura que `loading` siempre se desactive, incluso con error
> - `Promise.all` carga clasificación y usuarios en paralelo, más rápido que uno tras otro

---

## 5. Orden de Implementación

| Paso | Acción | Archivos | Tiempo estimado |
|------|--------|----------|-----------------|
| 1 | Crear tipos | `types/league.api.types.ts` | ~15 min |
| 2 | Crear capa API | `api/leagues.api.ts` | ~30 min |
| 3 | Crear service | `services/leagueService.ts` | ~30 min |
| 4 | Crear hook | `hooks/useLeagues.ts` | ~30 min |
| 5 | Conectar clasificación | `app/league/classification.tsx` | ~45 min |
| 6 | Conectar equipos | `app/league/teams.tsx` | ~45 min |
| 7 | Conectar usuarios | `app/league/users.tsx` | ~30 min |

**Total estimado: ~3.5 horas**

---

## 6. Notas Adicionales

- **Active League Store**: La app usa `activeLeagueStore` para gestionar la liga activa
- **Roles de usuario**: Asegurar compatibilidad entre backend (`entrenador`) y frontend (`coach`)
- **Imágenes**: El backend devuelve URLs, los componentes usan `require()` local
