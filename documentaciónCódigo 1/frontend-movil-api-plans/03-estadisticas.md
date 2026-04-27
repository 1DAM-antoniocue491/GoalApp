# Plan de Implementación: Estadísticas

## 1. Estado Actual

### Archivos existentes

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `src/app/(tabs)/statistics.tsx` | UI Only | Pantalla principal de estadísticas |
| `src/app/statistics/match.tsx` | UI Only | Estadísticas de partido (hardcodeado) |
| `src/app/statistics/players.tsx` | UI Only | Estadísticas de jugadores (hardcodeado) |
| `src/features/statistics/components/*.tsx` | UI Only | Componentes visuales (MVPsSection, TopScorersTable, etc.) |
| `src/features/statistics/api/statistics.api.ts` | **Vacío** | Sin implementación |
| `src/features/statistics/hooks/useStatistics.ts` | **Vacío** | Sin implementación |
| `src/features/statistics/services/statisticsService.ts` | **Vacío** | Sin implementación |
| `src/features/statistics/types/statistics.types.ts` | **Vacío** | Sin tipos |

### Datos actuales

- **Estadísticas de equipo**: Goles (30), Victorias/Empates/Derrotas (10 cada uno) hardcodeados
- **Goleadores**: Lista estática con "Marc Roca" y 20 goles
- **Estadísticas de jugador**: "Cucho Hernández" con datos fijos
- **MVP**: Sin implementación real

### Qué falta implementar

1. Conectar API de estadísticas de temporada (`GET /estadisticas/liga/{liga_id}/temporada`)
2. Conectar API de goleadores (`GET /estadisticas/liga/{liga_id}/goleadores`)
3. Conectar API de MVP (`GET /estadisticas/liga/{liga_id}/mvp`)
4. Conectar API de estadísticas personales (`GET /estadisticas/liga/{liga_id}/jugador/{usuario_id}/estadisticas`)
5. Conectar API de goles por equipo (`GET /estadisticas/liga/{liga_id}/equipos/goles`)

---

## 2. Endpoints del Backend

| Endpoint | Método | Existe | Datos que devuelve |
|----------|--------|--------|-------------------|
| `GET /estadisticas/liga/{liga_id}/temporada` | GET | ✅ | Stats generales (`SeasonStatsResponse`) |
| `GET /estadisticas/liga/{liga_id}/goleadores` | GET | ✅ | Lista de goleadores (`TopScorerResponse[]`) |
| `GET /estadisticas/liga/{liga_id}/mvp` | GET | ✅ | MVP de temporada (`MatchdayMVPResponse`) |
| `GET /estadisticas/liga/{liga_id}/jugador/{usuario_id}/estadisticas` | GET | ✅ | Stats personales (`PlayerPersonalStatsResponse`) |
| `GET /estadisticas/liga/{liga_id}/equipos/goles` | GET | ✅ | Stats de goles por equipo (`TeamGoalsStatsResponse[]`) |

### Endpoints que faltan en el backend

No faltan endpoints. El backend tiene completa la API de estadísticas.

---

## 3. Estructura de Archivos a Crear/Completar

```
src/features/statistics/
├── api/statistics.api.ts       # COMPLETAR
├── types/statistics.types.ts   # COMPLETAR
├── hooks/useStatistics.ts      # COMPLETAR
└── services/statisticsService.ts # COMPLETAR
```

---

## 4. Código de Ejemplo

### 4.1 Tipos (`types/statistics.types.ts`)

```typescript
/**
 * Tipos para estadísticas
 * Basados en app/schemas/estadisticas.py
 */

export interface SeasonStatsResponse {
  total_partidos: number;
  total_goles: number;
  promedio_goles_por_partido: number;
  total_amarillas: number;
  total_rojas: number;
  total_asistencias: number;
  equipos_participantes: number;
  jugadores_registrados: number;
}

export interface TopScorerResponse {
  id_jugador: number;
  id_usuario: number;
  id_equipo: number;
  nombre: string;
  nombre_equipo: string;
  escudo_equipo: string | null;
  goles: number;
  partidos_jugados: number;
  promedio_goles: number;
}

export interface MatchdayMVPResponse {
  id_jugador: number;
  id_usuario: number;
  nombre: string;
  nombre_equipo: string;
  escudo_equipo: string | null;
  rating: number;
  goles: number;
  asistencias: number;
  jornada: number;
}

export interface PlayerPersonalStatsResponse {
  id_jugador: number;
  id_usuario: number;
  nombre: string;
  nombre_equipo: string;
  escudo_equipo: string | null;
  goles: number;
  asistencias: number;
  tarjetas_amarillas: number;
  tarjetas_rojas: number;
  partidos_jugados: number;
  veces_mvp: number;
}

export interface TeamGoalsStatsResponse {
  id_equipo: number;
  nombre: string;
  escudo: string | null;
  goles_favor: number;
  goles_contra: number;
  diferencia_goles: number;
  promedio_goles_favor: number;
  partidos_jugados: number;
}
```

> **💡 Por qué este archivo:**
> - Cada interfaz corresponde a un endpoint específico del backend de estadísticas
> - `| null` en campos como `escudo_equipo` previene crashes si el backend devuelve `null`
> - Los nombres coinciden exactamente con el backend (`goles_favor` no `goalsFor`) para evitar bugs de mapeo
> - **Sin esto:** TypeScript no podría validar que estás usando los campos correctos en los componentes
>
> **💡 Consejo:**
> - El comentario `/** Basados en app/schemas/estadisticas.py */` documenta el origen de los tipos
> - Si el backend añade un campo nuevo, TypeScript te avisará dónde actualizar el frontend

### 4.2 Capa API (`api/statistics.api.ts`)

```typescript
import { apiClient } from '@/src/shared/api/client';
import type {
  SeasonStatsResponse,
  TopScorerResponse,
  MatchdayMVPResponse,
  PlayerPersonalStatsResponse,
  TeamGoalsStatsResponse,
} from '../types/statistics.types';

/**
 * GET /estadisticas/liga/{ligaId}/temporada - Stats generales
 */
export async function getSeasonStats(ligaId: number): Promise<SeasonStatsResponse> {
  const response = await apiClient.get<SeasonStatsResponse>(
    `/estadisticas/liga/${ligaId}/temporada`
  );
  return response.data;
}

/**
 * GET /estadisticas/liga/{ligaId}/goleadores - Top goleadores
 */
export async function getTopScorers(
  ligaId: number,
  limit = 5
): Promise<TopScorerResponse[]> {
  const response = await apiClient.get<TopScorerResponse[]>(
    `/estadisticas/liga/${ligaId}/goleadores?limit=${limit}`
  );
  return response.data;
}

/**
 * GET /estadisticas/liga/{ligaId}/mvp - MVP de temporada
 */
export async function getSeasonMVP(ligaId: number): Promise<MatchdayMVPResponse | null> {
  const response = await apiClient.get<MatchdayMVPResponse | null>(
    `/estadisticas/liga/${ligaId}/mvp`
  );
  return response.data;
}

/**
 * GET /estadisticas/liga/{ligaId}/jugador/{usuarioId}/estadisticas - Stats personales
 */
export async function getPlayerStats(
  ligaId: number,
  usuarioId: number
): Promise<PlayerPersonalStatsResponse | null> {
  const response = await apiClient.get<PlayerPersonalStatsResponse | null>(
    `/estadisticas/liga/${ligaId}/jugador/${usuarioId}/estadisticas`
  );
  return response.data;
}

/**
 * GET /estadisticas/liga/{ligaId}/equipos/goles - Stats de goles por equipo
 */
export async function getTeamGoalsStats(
  ligaId: number
): Promise<TeamGoalsStatsResponse[]> {
  const response = await apiClient.get<TeamGoalsStatsResponse[]>(
    `/estadisticas/liga/${ligaId}/equipos/goles`
  );
  return response.data;
}
```

> **💡 Por qué esta capa:**
> - Cada endpoint de estadísticas tiene su función nombrada claramente (`getTopScorers`, `getSeasonMVP`)
> - El parámetro `limit = 5` en `getTopScorers` permite controlar cuántos goleadores traer (útil para listas cortas)
> - `| null` en el retorno de `getSeasonMVP` y `getPlayerStats` indica que el backend puede no tener datos
> - **Sin esto:** Tendrías que construir las URLs manualmente en cada componente, propenso a errores
>
> **💡 Consejo:**
> - Si un endpoint devuelve 404 (ej: no hay MVP aún), el `| null` te obliga a manejar ese caso
> - Los JSDoc comments ayudan a encontrar rápido qué función llama a qué endpoint

### 4.3 Service (`services/statisticsService.ts`)

```typescript
import {
  getSeasonStats,
  getTopScorers,
  getSeasonMVP,
  getPlayerStats,
  getTeamGoalsStats,
} from '../api/statistics.api';
import type {
  SeasonStatsResponse,
  TopScorerResponse,
  MatchdayMVPResponse,
  PlayerPersonalStatsResponse,
  TeamGoalsStatsResponse,
} from '../types/statistics.types';

/**
 * Obtiene todas las estadísticas de temporada
 */
export async function fetchSeasonStats(ligaId: number): Promise<SeasonStatsResponse> {
  return getSeasonStats(ligaId);
}

/**
 * Obtiene top goleadores
 */
export async function fetchTopScorers(
  ligaId: number,
  limit = 5
): Promise<TopScorerResponse[]> {
  return getTopScorers(ligaId, limit);
}

/**
 * Obtiene MVP de temporada
 */
export async function fetchSeasonMVP(ligaId: number): Promise<MatchdayMVPResponse | null> {
  return getSeasonMVP(ligaId);
}

/**
 * Obtiene estadísticas personales de un jugador
 */
export async function fetchPlayerStats(
  ligaId: number,
  usuarioId: number
): Promise<PlayerPersonalStatsResponse | null> {
  return getPlayerStats(ligaId, usuarioId);
}

/**
 * Obtiene stats de goles por equipo
 */
export async function fetchTeamGoalsStats(
  ligaId: number
): Promise<TeamGoalsStatsResponse[]> {
  return getTeamGoalsStats(ligaId);
}
```

> **💡 Por qué esta capa:**
> - Los nombres `fetch*` indican claramente que son funciones asíncronas que traen datos
> - Esta capa puede añadir transformación de datos después (ej: calcular porcentajes) sin tocar la API
> - Centraliza la lógica de estadísticas, fácil de testear sin mocking de HTTP
> - **Sin esto:** Los componentes llamarían directamente a la API, mezclando concerns de UI y datos
>
> **💡 Consejo:**
> - Aunque ahora solo delegan, tener esta capa te permite añadir caché o memoización después
> - Los JSDoc en español ayudan a entender rápido qué hace cada función sin leer la implementación

### 4.4 Hook (`hooks/useStatistics.ts`)

```typescript
import { useState, useEffect } from 'react';
import {
  fetchSeasonStats,
  fetchTopScorers,
  fetchSeasonMVP,
  fetchPlayerStats,
  fetchTeamGoalsStats,
} from '../services/statisticsService';
import type {
  SeasonStatsResponse,
  TopScorerResponse,
  MatchdayMVPResponse,
  PlayerPersonalStatsResponse,
  TeamGoalsStatsResponse,
} from '../types/statistics.types';

interface UseStatisticsResult {
  seasonStats: SeasonStatsResponse | null;
  topScorers: TopScorerResponse[];
  mvp: MatchdayMVPResponse | null;
  teamGoalsStats: TeamGoalsStatsResponse[];
  playerStats: PlayerPersonalStatsResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useStatistics(
  ligaId: number,
  usuarioId?: number
): UseStatisticsResult {
  const [seasonStats, setSeasonStats] = useState<SeasonStatsResponse | null>(null);
  const [topScorers, setTopScorers] = useState<TopScorerResponse[]>([]);
  const [mvp, setMvp] = useState<MatchdayMVPResponse | null>(null);
  const [teamGoalsStats, setTeamGoalsStats] = useState<TeamGoalsStatsResponse[]>([]);
  const [playerStats, setPlayerStats] = useState<PlayerPersonalStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [stats, scorers, mvpData, teamStats] = await Promise.all([
        fetchSeasonStats(ligaId),
        fetchTopScorers(ligaId, 5),
        fetchSeasonMVP(ligaId),
        fetchTeamGoalsStats(ligaId),
      ]);

      setSeasonStats(stats);
      setTopScorers(scorers);
      setMvp(mvpData);
      setTeamGoalsStats(teamStats);

      if (usuarioId) {
        const pStats = await fetchPlayerStats(ligaId, usuarioId);
        setPlayerStats(pStats);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ligaId) {
      loadData();
    }
  }, [ligaId, usuarioId]);

  return {
    seasonStats,
    topScorers,
    mvp,
    teamGoalsStats,
    playerStats,
    loading,
    error,
    refresh: loadData,
  };
}
```

> **💡 Por qué este hook:**
> - Carga 4 estadísticas en paralelo con `Promise.all`, más rápido que una tras otra
> - `usuarioId` es opcional: las stats personales solo se cargan si se pasa un usuario
> - La condición `if (ligaId)` en `useEffect` evita llamadas inválidas cuando no hay liga seleccionada
> - **Sin esto:** Cada componente de estadísticas repetiría la lógica de carga múltiple y manejo de estados
>
> **💡 Consejo:**
> - `| null` en `seasonStats` y `mvp` obliga a la UI a manejar el caso "sin datos"
> - El retorno incluye `refresh` para recargar stats tras una actualización (ej: tras registrar un gol)

---

## 5. Orden de Implementación

| Paso | Acción | Archivos | Tiempo estimado |
|------|--------|----------|-----------------|
| 1 | Crear tipos | `types/statistics.types.ts` | ~20 min |
| 2 | Crear capa API | `api/statistics.api.ts` | ~30 min |
| 3 | Crear service | `services/statisticsService.ts` | ~30 min |
| 4 | Crear hook | `hooks/useStatistics.ts` | ~30 min |
| 5 | Conectar StatisticsScreen | `features/statistics/components/StatisticsScreen.tsx` | ~45 min |
| 6 | Conectar TopScorersTable | `features/statistics/components/TopScorersTable.tsx` | ~30 min |
| 7 | Conectar MVPsSection | `features/statistics/components/MVPsSection.tsx` | ~30 min |

**Total estimado: ~3.5 horas**

---

## 6. Notas Adicionales

- **Rating del MVP**: El backend calcula rating como `7.0 + (goles + asistencias) * 0.3`
- **Jornada**: El MVP devuelve `jornada: 1` siempre (temporada completa). El frontend puede necesitar agrupar por jornada real.
- **Imágenes de escudos**: El backend devuelve URLs, asegurar que los componentes las rendericen correctamente.
