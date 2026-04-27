# Plan de Implementación: Partidos

## 1. Estado Actual

### Archivos existentes

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `src/app/matches/Live.tsx` | UI Only | Partidos en vivo con datos hardcodeados |
| `src/app/matches/Programmed.tsx` | UI Only | Partidos programados con datos hardcodeados |
| `src/app/matches/Finished.tsx` | UI Only | Partidos finalizados con datos hardcodeados |
| `src/app/match/all_finished/alignment.tsx` | UI Only | Alineaciones (hardcodeado) |
| `src/app/match/all_finished/statistics.tsx` | UI Only | Estadísticas del partido |
| `src/app/match/all_programmed/previousMeetings.tsx` | UI Only | Enfrentamientos previos |
| `src/app/match/all_programmed/squad.tsx` | UI Only | Plantillas del partido |
| `src/features/matches/components/*.tsx` | UI Only | Componentes visuales |
| `src/features/matches/api/matches.api.ts` | **Vacío** | Sin implementación |
| `src/features/matches/hooks/useMatches.ts` | **Vacío** | Sin implementación |
| `src/features/matches/services/matchesService.ts` | **Vacío** | Sin implementación |
| `src/features/matches/types/matches.types.ts` | **Vacío** | Sin tipos |

### Datos actuales

- **Partidos en vivo**: Resultado 2-1 hardcodeado entre Betis y Real Madrid
- **Partidos programados**: Fecha y hora hardcodeadas (21:00, 13 de Marzo)
- **Partidos finalizados**: Resultado estático 2-1
- **Estadio**: "Estadio La Cartuja" hardcodeado

### Qué falta implementar

1. Conectar API de partidos en vivo (`GET /partidos/en-vivo`)
2. Conectar API de próximos partidos (`GET /partidos/proximos`)
3. Conectar API de partidos por liga (`GET /partidos/ligas/{liga_id}/con-equipos`)
4. Implementar detalles de partido con estadísticas
5. Implementar alineaciones desde backend

---

## 2. Endpoints del Backend

| Endpoint | Método | Existe | Datos que devuelve |
|----------|--------|--------|-------------------|
| `GET /partidos/` | GET | ✅ | Lista de partidos (`PartidoResponse[]`) |
| `GET /partidos/en-vivo` | GET | ✅ | Partidos en vivo (`PartidoConEquipos[]`) |
| `GET /partidos/proximos` | GET | ✅ | Próximos partidos (`PartidoConEquipos[]`) |
| `GET /partidos/ligas/{liga_id}/con-equipos` | GET | ✅ | Partidos con info de equipos |
| `GET /partidos/ligas/{liga_id}/jornadas` | GET | ✅ | Partidos agrupados por jornada |
| `GET /partidos/{partido_id}` | GET | ✅ | Detalle de partido |
| `PUT /partidos/{partido_id}/iniciar` | PUT | ✅ | Iniciar partido |
| `PUT /partidos/{partido_id}/finalizar` | PUT | ✅ | Finalizar partido |

### Endpoints que faltan en el backend

- `GET /partidos/{partido_id}/alineaciones` - No existe, necesitaría crearse
- `GET /partidos/{partido_id}/enfrentamientos-previos` - No existe, necesitaría crearse

---

## 3. Estructura de Archivos a Crear/Completar

```
src/features/matches/
├── api/matches.api.ts          # COMPLETAR
├── types/matches.types.ts      # COMPLETAR
├── hooks/useMatches.ts         # COMPLETAR
└── services/matchesService.ts  # COMPLETAR
```

---

## 4. Código de Ejemplo

### 4.1 Tipos (`types/matches.types.ts`)

```typescript
export type MatchStatus = 'programado' | 'en_juego' | 'finalizado' | 'cancelado';

export interface PartidoResponse {
  id_partido: number;
  id_liga: number;
  id_equipo_local: number;
  id_equipo_visitante: number;
  fecha: string; // ISO 8601
  estado: MatchStatus;
  goles_local: number | null;
  goles_visitante: number | null;
  created_at: string;
  updated_at: string;
}

export interface PartidoConEquipos extends PartidoResponse {
  equipo_local: {
    id_equipo: number;
    nombre: string;
    escudo: string | null;
  };
  equipo_visitante: {
    id_equipo: number;
    nombre: string;
    escudo: string | null;
  };
}

export interface JornadaConPartidos {
  jornada: number;
  partidos: PartidoConEquipos[];
}

export interface AlineacionResponse {
  id_alineacion: number;
  id_partido: number;
  id_equipo: number;
  id_jugador: number;
  es_titular: boolean;
  dorsal: number;
  posicion: string;
}
```

> **💡 Por qué este archivo:**
> - `MatchStatus` como union type te da autocompletado y evita errores de escritura ('live' vs 'en_juego')
> - `PartidoConEquipos` extiende `PartidoResponse` porque el backend devuelve los equipos anidados cuando pides partidos con equipos
> - Los campos `goles_local | null` reflejan que un partido programado aún no tiene goles
> - **Sin esto:** No sabrías qué campos existen hasta probarlo, y podrías acceder a `equipo_local.nombre` cuando es `undefined`
>
> **💡 Consejo:**
> - El tipo `| null` es explícito: el backend puede devolver `null`, no `undefined`
> - `JornadaConPartidos` agrupa partidos por jornada, útil para renderizar secciones en la UI

### 4.2 Capa API (`api/matches.api.ts`)

```typescript
import { apiClient } from '@/src/shared/api/client';
import type {
  PartidoResponse,
  PartidoConEquipos,
  JornadaConPartidos,
} from '../types/matches.types';

/**
 * GET /partidos/en-vivo - Partidos en vivo
 */
export async function getLiveMatches(): Promise<PartidoConEquipos[]> {
  const response = await apiClient.get<PartidoConEquipos[]>('/partidos/en-vivo');
  return response.data;
}

/**
 * GET /partidos/proximos - Próximos partidos
 */
export async function getUpcomingMatches(limit = 10): Promise<PartidoConEquipos[]> {
  const response = await apiClient.get<PartidoConEquipos[]>(
    `/partidos/proximos?limit=${limit}`
  );
  return response.data;
}

/**
 * GET /partidos/ligas/{ligaId}/con-equipos - Partidos de una liga con equipos
 */
export async function getMatchesByLeague(
  ligaId: number
): Promise<PartidoConEquipos[]> {
  const response = await apiClient.get<PartidoConEquipos[]>(
    `/partidos/ligas/${ligaId}/con-equipos`
  );
  return response.data;
}

/**
 * GET /partidos/ligas/{ligaId}/jornadas - Partidos por jornada
 */
export async function getMatchesByJourney(
  ligaId: number
): Promise<JornadaConPartidos[]> {
  const response = await apiClient.get<JornadaConPartidos[]>(
    `/partidos/ligas/${ligaId}/jornadas`
  );
  return response.data;
}

/**
 * GET /partidos/{matchId} - Detalle de partido
 */
export async function getMatchById(matchId: number): Promise<PartidoResponse> {
  const response = await apiClient.get<PartidoResponse>(`/partidos/${matchId}`);
  return response.data;
}
```

> **💡 Por qué esta capa:**
> - Cada endpoint tiene su función específica, clara de leer y testear individualmente
> - Los JSDoc comments (`/** ... */`) documentan qué hace cada función sin tener que leer el código
> - El parámetro `limit = 10` en `getUpcomingMatches` tiene valor por defecto, útil si no necesitas todos los partidos
> - **Sin esto:** Tendrías URLs de endpoints dispersas por el código, difícil de rastrear cambios
>
> **💡 Consejo:**
> - Los endpoints de partidos en vivo y próximos ya incluyen los equipos, por eso usan `PartidoConEquipos`
> - `getMatchesByJourney` devuelve la estructura agrupada que el backend ya prepara, ahorra trabajo en el frontend

### 4.3 Service (`services/matchesService.ts`)

```typescript
import {
  getLiveMatches,
  getUpcomingMatches,
  getMatchesByLeague,
  getMatchesByJourney,
} from '../api/matches.api';
import type { PartidoConEquipos, JornadaConPartidos } from '../types/matches.types';

/**
 * Formatea fecha para mostrar en UI
 */
function formatMatchDate(fecha: string): { time: string; date: string } {
  const date = new Date(fecha);
  return {
    time: date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
    date: date.toLocaleDateString('es-ES', { day: 'numeric', month: 'long' }),
  };
}

/**
 * Obtiene partidos en vivo formateados
 */
export async function fetchLiveMatches(): Promise<PartidoConEquipos[]> {
  return getLiveMatches();
}

/**
 * Obtiene próximos partidos formateados
 */
export async function fetchUpcomingMatches(limit = 10): Promise<PartidoConEquipos[]> {
  return getUpcomingMatches(limit);
}

/**
 * Obtiene partidos de una liga agrupados por jornada
 */
export async function fetchMatchesByJourney(
  ligaId: number
): Promise<JornadaConPartidos[]> {
  return getMatchesByJourney(ligaId);
}
```

> **💡 Por qué esta capa:**
> - `formatMatchDate` centraliza el formateo de fechas, consistente en toda la app (ej: "13 de marzo, 21:00")
> - Las funciones del service pueden añadir lógica adicional (validación, caché) sin tocar la capa API
> - Separa concerns: API hace HTTP, Service transforma/prepara datos
> - **Sin esto:** Cada componente formatearía fechas a su manera, inconsistente para el usuario
>
> **💡 Consejo:**
> - Aunque ahora solo delegan a la API, tener esta capa te permite añadir caché o retry logic después
> - `formatMatchDate` no se exporta porque es un helper interno, solo las funciones `fetch*` son públicas

### 4.4 Hook (`hooks/useMatches.ts`)

```typescript
import { useState, useEffect } from 'react';
import {
  fetchLiveMatches,
  fetchUpcomingMatches,
  fetchMatchesByJourney,
} from '../services/matchesService';
import type { PartidoConEquipos, JornadaConPartidos } from '../types/matches.types';

interface UseMatchesResult {
  liveMatches: PartidoConEquipos[];
  upcomingMatches: PartidoConEquipos[];
  matchesByJourney: JornadaConPartidos[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useMatches(ligaId?: number): UseMatchesResult {
  const [liveMatches, setLiveMatches] = useState<PartidoConEquipos[]>([]);
  const [upcomingMatches, setUpcomingMatches] = useState<PartidoConEquipos[]>([]);
  const [matchesByJourney, setMatchesByJourney] = useState<JornadaConPartidos[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [live, upcoming] = await Promise.all([
        fetchLiveMatches(),
        fetchUpcomingMatches(10),
      ]);
      setLiveMatches(live);
      setUpcomingMatches(upcoming);

      if (ligaId) {
        const journeyMatches = await fetchMatchesByJourney(ligaId);
        setMatchesByJourney(journeyMatches);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar partidos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [ligaId]);

  return {
    liveMatches,
    upcomingMatches,
    matchesByJourney,
    loading,
    error,
    refresh: loadData,
  };
}
```

> **💡 Por qué este hook:**
> - Carga partidos en vivo y próximos en paralelo con `Promise.all`, más rápido que secuencial
> - `ligaId` es opcional: si no se pasa, solo carga live/upcoming, no los de la liga específica
> - El estado se gestiona fuera del componente, reutilizable en Live.tsx, Programmed.tsx, Finished.tsx
> - **Sin esto:** Cada pantalla de partidos repetiría la misma lógica de carga y manejo de errores
>
> **💡 Consejo:**
> - `refresh: loadData` permite a la UI recargar datos tras una acción (ej: tras crear un partido)
> - El array de dependencias `[ligaId]` en `useEffect` recarga datos si cambia la liga seleccionada

---

## 5. Orden de Implementación

| Paso | Acción | Archivos | Tiempo estimado |
|------|--------|----------|-----------------|
| 1 | Crear tipos | `types/matches.types.ts` | ~20 min |
| 2 | Crear capa API | `api/matches.api.ts` | ~30 min |
| 3 | Crear service | `services/matchesService.ts` | ~30 min |
| 4 | Crear hook | `hooks/useMatches.ts` | ~30 min |
| 5 | Conectar Live | `app/matches/Live.tsx` | ~45 min |
| 6 | Conectar Programmed | `app/matches/Programmed.tsx` | ~45 min |
| 7 | Conectar Finished | `app/matches/Finished.tsx` | ~45 min |

**Total estimado: ~4 horas**

---

## 6. Notas Adicionales

- **Estado del partido**: El backend usa `programado`, `en_juego`, `finalizado`. El frontend usa `live`, `programmed`, `finished`. Mapear correctamente.
- **Alineaciones**: El backend tiene modelo `AlineacionPartido` pero no hay endpoint específico. Necesitaría crearse `GET /partidos/{id}/alineaciones`.
- **Enfrentamientos previos**: Requiere endpoint nuevo que calcule historial entre dos equipos.
