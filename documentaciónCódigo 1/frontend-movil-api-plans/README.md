# Planes de Implementación - Frontend Móvil GoalApp

## Resumen

| Feature | Estado | Endpoints necesarios | Complejidad |
|---------|--------|---------------------|-------------|
| Liga | 📁 Solo UI | 6 endpoints | 🟡 Media |
| Partidos | 📁 Solo UI | 7 endpoints | 🟡 Media |
| Estadísticas | 📁 Solo UI | 5 endpoints | 🟢 Baja |
| Perfil | 🟡 Parcial | 5 endpoints | 🟢 Baja |
| Notificaciones | 🔴 Vacío | 6 endpoints | 🟡 Media |

**Leyenda:**
- 🟢 Baja - Implementación directa, sin dependencias
- 🟡 Media - Requiere integración con otras features
- 🔴 Alta - Requiere trabajo adicional significativo

---

## Orden Recomendado de Implementación

1. **Liga** - Base para otras features (clasificación, equipos)
2. **Partidos** - Depende de Liga (equipos, jornada)
3. **Estadísticas** - Depende de Partidos y Liga
4. **Perfil** - Independiente, usa auth existente
5. **Notificaciones** - Independiente, polling automático

---

## Planes Detallados

| Plan | Feature | Archivo | Tiempo Estimado |
|------|---------|---------|-----------------|
| [01-liga.md](01-liga.md) | Liga | `src/features/leagues/` | ~3.5 horas |
| [02-partidos.md](02-partidos.md) | Partidos | `src/features/matches/` | ~4 horas |
| [03-estadisticas.md](03-estadisticas.md) | Estadísticas | `src/features/statistics/` | ~3.5 horas |
| [04-perfil.md](04-perfil.md) | Perfil | `src/features/profile/` | ~2.5 horas |
| [05-notificaciones.md](05-notificaciones.md) | Notificaciones | `src/features/notifications/` | ~3 horas |

**Total estimado: ~16.5 horas**

---

## Patrón de Referencia

Usar `src/app/auth/api/auth.api.ts` como referencia de estilo:

```typescript
// Estructura consistente:
// 1. Imports de tipos
// 2. Constante BASE_URL (si aplica)
// 3. Funciones exportadas con JSDoc
// 4. Manejo de errores consistente
```

---

## Cliente HTTP Disponible

`src/shared/api/client.ts` - `apiClient` con:
- Inyección automática de token JWT
- Retry con backoff exponencial (3 intentos)
- Timeout configurable
- Manejo de errores con `ApiError`

```typescript
// Ejemplo de uso:
const response = await apiClient.get<User[]>('/usuarios/');
const data = response.data; // Tipo User[]
```

---

## Backend API Reference

Base URL: `https://goalapp-backend-j2cx.onrender.com/api/v1`

### Endpoints Principales

| Recurso | Endpoints |
|---------|-----------|
| Ligas | `GET /ligas/`, `GET /ligas/{id}`, `GET /ligas/{id}/clasificacion` |
| Partidos | `GET /partidos/en-vivo`, `GET /partidos/proximos`, `GET /partidos/ligas/{id}/con-equipos` |
| Estadísticas | `GET /estadisticas/liga/{id}/temporada`, `GET /estadisticas/liga/{id}/goleadores`, `GET /estadisticas/liga/{id}/mvp` |
| Usuarios | `GET /usuarios/me`, `PUT /usuarios/{id}` |
| Notificaciones | `GET /notificaciones/`, `GET /notificaciones/no-leidas`, `PATCH /notificaciones/{id}/leer` |

---

## 📚 Guía Educativa: Entendiendo la Arquitectura

### ¿Por qué esta estructura de archivos?

El proyecto usa **4 capas** para conectar el frontend con el backend. Aquí explico por qué:

#### 1. Tipos (`types/*.types.ts`)

**¿Qué es?** Archivos con interfaces TypeScript que describen los datos.

**¿Por qué existe?**
- El backend devuelve datos con una estructura específica (ej: `id_liga`, `nombre`, `temporada`)
- TypeScript necesita saber esa estructura para dar autocompletado y detectar errores
- Si el backend cambia un campo, TypeScript te avisa en el editor

**¿Qué pasaría sin esto?**
- No tendrías autocompletado al escribir `league.` o `match.`
- Errores solo se descubren en tiempo de ejecución (cuando la app falla)
- Más difícil de mantener

**Ejemplo genérico:**
```typescript
// Con tipos - sabes qué campos existen
const data: ApiResponse = {
  id: 1,
  nombre: "Liga 1",
  activa: true,  // ← TypeScript te avisa si escribes "active" en vez de "activa"
};
```

---

#### 2. Capa API (`api/*.api.ts`)

**¿Qué es?** Funciones que hacen las llamadas HTTP al backend.

**¿Por qué existe?**
- Centraliza todas las llamadas en un solo lugar
- Maneja errores de red y HTTP de forma consistente
- Usa `apiClient` que inyecta el token de autenticación automáticamente

**¿Por qué no llamar al backend desde el componente?**
- Si llamas `fetch()` directamente en cada componente, el código se duplica
- Si cambia la URL del endpoint, tienes que cambiar 10 archivos
- No manejas errores de forma consistente

**Ejemplo genérico:**
```typescript
// MAL - Llamada directa desde componente
function DataList() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/endpoint')  // ← URL hardcodeada
      .then(res => res.json())
      .then(setData);
  }, []);
  
  // ¿Qué pasa si hay error de red?
  // ¿Qué pasa si necesitas el token de auth?
  // ¿Qué pasa si la URL cambia?
}

// BIEN - Usando capa API
function DataList() {
  const { data, loading, error } = useData();
  // ← Todo manejado: loading, error, datos tipados
}
```

---

#### 3. Service (`services/*Service.ts`)

**¿Qué es?** Lógica de negocio entre la API y el hook.

**¿Por qué existe?**
- Transforma datos del backend al formato que necesita el frontend
- Agrupa múltiples llamadas de API si es necesario
- Permite reutilizar lógica entre diferentes hooks

**¿Es siempre necesario?**
- Para cosas simples, puedes saltártelo
- Para cosas complejas (transformar datos, combinar múltiples endpoints), es esencial

**Ejemplo genérico:**
```typescript
// El backend devuelve campos en un formato
// El frontend quiere otro formato para la UI

// Service transforma los datos
function transformData(backendData: BackendResponse): FrontendData {
  return {
    id: String(backendData.id),           // ← Transforma número a string
    name: backendData.nombre,             // ← Renombra campo
    status: backendData.activa ? 'active' : 'finished',  // ← Convierte boolean a enum
  };
}
```

---

#### 4. Hook (`hooks/use*.ts`)

**¿Qué es?** Hook de React que gestiona estado y llama al service.

**¿Por qué existe?**
- Gestiona estados: `loading`, `error`, `data`
- Se ejecuta automáticamente cuando cambian las dependencias (`useEffect`)
- El componente solo se preocupa de renderizar, no de cargar datos

**¿Qué problema resuelve?**
Sin hook, cada componente tendría que hacer:
```typescript
// MAL - Cada componente repite esta lógica
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  setLoading(true);
  apiCall()
    .then(setData)
    .catch(setError)
    .finally(() => setLoading(false));
}, []);
```

Con hook:
```typescript
// BIEN - Lógica reutilizable
const { data, loading, error, refresh } = useData();
```

---

### Flujo de Datos Completo

Así viajan los datos desde el backend hasta tu componente:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BACKEND devuelve datos                                  │
│    GET /api/endpoint → [{ id: 1, nombre: "Item", ... }]    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. API LAYER recibe y tipa                                 │
│    getData(): ApiResponse[]                                │
│    - Inyecta token automáticamente                         │
│    - Maneja errores HTTP                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. SERVICE transforma                                      │
│    fetchData() → FrontendData[]                            │
│    - Transforma campos del backend al formato frontend     │
│    - Agrupa múltiples llamadas si es necesario             │
│    - Calcula datos derivados                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. HOOK gestiona estado                                    │
│    useData() → { data, loading, error, refresh }           │
│    - useState para guardar datos                           │
│    - useEffect para cargar automáticamente                 │
│    - Maneja loading y error                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. COMPONENTE renderiza                                    │
│    {loading ? <Loader /> : data.map(item => <Card {...item} />)} │
└─────────────────────────────────────────────────────────────┘
```

---

### Errores Comunes de Principiantes (y cómo evitarlos)

#### ❌ Error 1: Hacer fetch directamente en el componente

```typescript
// MAL
function DataList() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('https://api.example.com/endpoint')  // ← URL hardcodeada
      .then(res => res.json())
      .then(setData);
  }, []);
  
  return <div>{data.map(item => item.name)}</div>;
}

// Problemas:
// - No maneja errores
// - No maneja loading
// - URL hardcodeada
// - Sin autenticación
// - Sin reutilización
```

#### ✅ Solución: Usar hook personalizado

```typescript
function DataList() {
  const { data, loading, error } = useData();
  
  if (loading) return <Loader />;
  if (error) return <Error message={error} />;
  
  return <div>{data.map(item => <Card key={item.id} item={item} />)}</div>;
}
```

---

#### ❌ Error 2: No manejar estados de loading y error

```typescript
// MAL
function DataList() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    getData().then(setData);  // ← ¿Y si falla?
  }, []);
  
  return <div>{data.map(item => item.name)}</div>;  // ← ¿Y si está cargando?
}
```

#### ✅ Solución: Manejar todos los estados

```typescript
function DataList() {
  const { data, loading, error } = useData();
  
  if (loading) return <Loader />;
  if (error) return <ErrorMessage error={error} />;
  if (data.length === 0) return <EmptyState />;
  
  return <div>{data.map(item => <Card key={item.id} item={item} />)}</div>;
}
```

---

#### ❌ Error 3: No tipar las respuestas

```typescript
// MAL
function useData() {
  const [data, setData] = useState([]);  // ← ¿Qué tipo es esto?
  // TypeScript no sabe qué campos tienen los datos
  // No hay autocompletado
  // Errores solo en runtime
}
```

#### ✅ Solución: Tipar explícitamente

```typescript
// BIEN
interface ApiResponse {
  id: number;
  name: string;
  active: boolean;
}

function useData() {
  const [data, setData] = useState<ApiResponse[]>([]);
  // ← TypeScript sabe la estructura
  // ← Autocompletado: data[0].id, data[0].name
  // ← Errores en compile time
}
```

---

#### ❌ Error 4: Múltiples llamadas sin controlar

```typescript
// MAL - Llama varias veces a la API en paralelo sin control
function Dashboard() {
  useEffect(() => {
    getData();
    getStats();
    getUsers();
  }, []);
}
```

#### ✅ Solución: Controlar llamadas paralelas

```typescript
// BIEN
function Dashboard() {
  useEffect(() => {
    async function loadData() {
      try {
        const [data, stats, users] = await Promise.all([
          getData(),
          getStats(),
          getUsers(),
        ]);
        // Todos cargados a la vez
      } catch (error) {
        // Maneja error de cualquiera
      }
    }
    loadData();
  }, []);
}
```

---

#### ❌ Error 5: Actualizar estado incorrectamente (mutación directa)

```typescript
// MAL - Mutación directa del estado
function updateItem(id: number) {
  const item = items.find(i => i.id === id);
  item.active = true;  // ← ¡Mutación directa! React no detecta el cambio
  setItems(items);
}
```

#### ✅ Solución: Actualizar estado inmutablemente

```typescript
// BIEN - Crear nuevo array con map
function updateItem(id: number) {
  setItems(prev =>
    prev.map(i => i.id === id ? { ...i, active: true } : i)
  );
}
```

---

#### ❌ Error 6: No hacer polling cuando se necesitan actualizaciones

```typescript
// MAL - Solo carga al montar, nunca se actualiza
function useNotifications() {
  useEffect(() => {
    loadData();  // ← Solo se ejecuta una vez
  }, []);
}
```

#### ✅ Solución: Polling para actualizaciones periódicas

```typescript
// BIEN - Polling cada 30 segundos
function useNotifications(refreshInterval = 30000) {
  useEffect(() => {
    loadData();
    
    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);  // ← Limpieza al desmontar
  }, [refreshInterval]);
}
```

---

### Glosario de Términos

| Término | Significado |
|---------|-------------|
| **Endpoint** | URL del backend que devuelve datos (ej: `/ligas/`, `/partidos/en-vivo`) |
| **API Layer** | Capa que centraliza las llamadas HTTP al backend |
| **Service** | Capa de lógica de negocio que transforma/agrupa datos |
| **Hook** | Función de React que gestiona estado y carga datos automáticamente |
| **TypeScript Interface** | Define la estructura/forma de los datos |
| **Promise** | Valor que puede estar disponible ahora o en el futuro (operación asíncrona) |
| **async/await** | Sintaxis para trabajar con Promises de forma legible |
| **Loading state** | Estado mientras se cargan datos desde el backend |
| **Error state** | Estado cuando ocurre un error en la carga de datos |
| **Polling** | Hacer la misma petición periódicamente para mantener datos actualizados |
| **Promise.all** | Ejecuta múltiples promesas en paralelo y espera a todas |
| **Optimistic update** | Actualizar UI antes de confirmar del backend (riesgoso) |
| **Immutable update** | Actualizar estado creando una copia, no mutando el original |

---

### Recursos para Aprender Más

- [React Hooks Documentation](https://react.dev/reference/react)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Fetch API vs Axios](https://javascript.info/fetch)
- [React Query - Alternative a hooks manuales](https://tanstack.com/query)
- [MDN Web Docs - Using Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)
- [MDN Web Docs - async/await](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
