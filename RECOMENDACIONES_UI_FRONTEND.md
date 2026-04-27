# 📋 Recomendaciones de Mejora UI/UX - GoalApp Frontend Web

**Fecha:** 2026-04-18  
**Proyecto:** GoalApp_Frontend_Web  
**Ubicación:** `GoalApp_Frontend_Web/goalapp-frontend/src/`

---

## Tabla de Contenidos

1. [Dashboards por Rol](#1--dashboards-por-rol)
2. [Onboarding](#2--onboarding)
3. [Páginas Secundarias](#3--páginas-secundarias)
4. [Auth](#4--auth)
5. [Public Dashboard](#5--public-dashboard)
6. [Navegación](#6--navegación)
7. [Prioridades de Implementación](#7--prioridades-de-implementación)

---

## 1. 🏠 Dashboards por Rol

### AdminDashboard (`src/features/main/components/dashboard/roles/AdminDashboard.tsx`)

**Estado actual:** Muestra 3 tarjetas de resumen (equipos, usuarios, partidos), partidos en vivo con marcador, resultados recientes, próximos partidos y botón flotante de configuración.

**Mejoras propuestas:**

#### 1.1 Gráficas de actividad
- **Línea de tiempo de goles por jornada:** Visualizar cómo evoluciona el número de goles a lo largo de las jornadas de la liga
- **Toggle de métricas:** Alternar entre ver goles, tarjetas u otras estadísticas acumuladas
- **Rango de tiempo:** Selector para ver datos de últimos 7 días, 30 días o toda la temporada

#### 1.2 Widget de notificaciones pendientes
- **Contador agrupado por tipo:** Mostrar cuántas notificaciones sin leer hay de cada categoría (convocatorias, partidos programados, resultados)
- **Expandir al hacer click:** Lista desplegable con las últimas 5 notificaciones no leídas
- **Acceso rápido:** Marcar como leída directamente desde el widget

#### 1.3 Accesos rápidos de administración
- **4 botones de acción directa:**
  - Invitar usuarios → abre formulario de invitación
  - Crear equipo → navega a creación de equipo
  - Configurar jornada → abre calendario de programación
  - Ver clasificación → navega a tabla de posiciones

#### 1.4 Filtro de vista
- **Toggle "Toda la liga" / "Mi equipo":** Si el admin también es entrenador de un equipo, poder filtrar para ver solo datos relevantes a su equipo
- **Badge identificador:** Mostrar qué equipo se está visualizando cuando el filtro está activo

#### 1.5 Estado de configuración de liga
- **Progress bar:** Mostrar porcentaje de configuración completada (ej: "60% completado")
- **Checklist visual:** Items como "Liga creada", "Temporada definida", "Equipos registrados", "Calendario publicado"
- **CTA:** Botón que lleva directamente a completar la configuración pendiente

---

### CoachDashboard (`src/features/main/components/dashboard/roles/CoachDashboard.tsx`)

**Estado actual:** 3 tarjetas de resumen (jugadores, partidos jugados, victorias), mismas secciones de partidos que el admin.

**Mejoras propuestas:**

#### 2.1 Próximo partido destacado
- **Card grande tipo héroe:** Ocupa el ancho completo, destaca visualmente
- **Contador regresivo:** "Faltan 3 días, 5 horas" que se actualiza automáticamente
- **Información completa:** Equipos, fecha/hora, estadio
- **Dos botones de acción:** "Ver convocatoria" y "Crear alineación"

#### 2.2 Estado de la plantilla
- **4 badges horizontales:**
  - 🟢 Disponibles (número)
  - 🟡 Lesionados (número, click muestra lista)
  - 🔴 Suspendidos (número, click muestra lista)
  - ⚪ No convocados (número)
- **Interactivo:** Click en cada badge muestra modal con nombres y detalles

#### 2.3 Estadísticas de equipo mejoradas
- **4 métricas clave:**
  - Posición en liga con subtexto "de X equipos"
  - Goles a favor con diferencia de goles
  - Goles en contra con ranking defensivo
  - Racha actual mostrando últimos 5 resultados (V-E-D)

#### 2.4 Botón rápido de convocatoria
- **Botón flotante:** Similar al de settings pero en posición inferior izquierda
- **Funcionalidad:** Abre modal para crear convocatoria de partido
- **Lista de jugadores:** Checkboxes para seleccionar convocados
- **Estado visible:** Badge mostrando "X de Y convocados"

#### 2.5 Formación recomendada
- **Análisis automático:** Basado en jugadores disponibles, sugiere formación óptima
- **Diagrama táctico:** Visualización simple del campo con posiciones
- **CTA:** Botón "Aplicar formación" que pre-llena la página de alineaciones

---

### PlayerDashboard ⚠️ **CRÍTICO - Datos hardcoded actualmente**

**Archivo:** `src/features/main/components/dashboard/roles/PlayerDashboard.tsx`

**Estado actual:** Muestra estadísticas genéricas de la liga (hardcoded en líneas 22-74), no datos personales del usuario.

**Mejoras propuestas:**

#### 3.1 Estadísticas personales reales
- **4 tarjetas con datos del usuario:** Goles, asistencias, partidos jugados, valoración promedio
- **Datos en tiempo real:** Conectados a la API del backend
- **Subtexto contextual:** Ej: "+12 de diferencia de goles" o "Media de 90 minutos por partido"

#### 3.2 Mi próximo partido
- **Card destacada:** Después de las estadísticas personales
- **Estado de convocatoria:** Badge grande que muestra "Sí / No / Pendiente"
- **Acción rápida:** Botón "Marcar asistencia" para confirmar presencia
- **Información:** Rival, fecha, hora, estadio

#### 3.3 Selector de estado personal
- **3 opciones tipo toggle:** Disponible / Lesionado / Suspendido
- **Campos adicionales:**
  - Si "Lesionado": tipo de lesión y fecha estimada de vuelta
  - Si "Suspendido": motivo (tarjetas acumuladas o expulsión directa)
- **Visible para:** El entrenador y delegado pueden ver el estado

#### 3.4 Historial personal de partidos
- **Tabla de últimos 5 partidos:** Rival, resultado, goles, asistencias, tarjetas, minutos jugados
- **Expandible:** Click en fila muestra detalles completos del partido
- **Métricas avanzadas:** Calorías, distancia recorrida, eventos clave

#### 3.5 Comparativa con la liga
- **Ranking contextual:** "Eres el 3º máximo goleador con 8 goles"
- **Top 5 visual:** Barras horizontales mostrando los líderes de la categoría
- **Highlight:** El usuario aparece resaltado en la lista
- **Múltiples métricas:** Toggle para ver goles, asistencias, valoración o tarjetas

---

### DelegateDashboard ⚠️ **CRÍTICO - Datos hardcoded actualmente**

**Archivo:** `src/features/main/components/dashboard/roles/DelegateDashboard.tsx`

**Estado actual:** Muestra partidos con botones de acción (Registrar Evento, Ver Plantillas, Finalizar, Iniciar) pero con datos ficticios (líneas 22-107).

**Mejoras propuestas:**

#### 4.1 Checklist pre-partido
- **Lista de verificación:** Jugadores convocados confirmados, alineaciones enviadas, campo verificado, árbitro presente
- **Validación:** Botón "Iniciar Partido" solo se habilita cuando todo está completado
- **Visual:** Checkboxes que se marcan al completar cada item

#### 4.2 Historial de eventos del partido
- **Timeline vertical:** Lista cronológica de eventos (goles, tarjetas, cambios)
- **Auto-actualización:** Polling cada 30 segundos si el partido está en vivo
- **Interactivo:** Click en evento muestra detalles del jugador y acción

#### 4.3 Contador de tiempo del partido
- **Reloj visible:** En header del dashboard, muestra minuto actual
- **Controles:** Iniciar, Pausar, Finalizar
- **Editable:** Posibilidad de corregir tiempo si hay error
- **Badge de estado:** "EN JUEGO", "DESCANSO", "FINALIZADO"

#### 4.4 Accesos por permisos dinámicos
- **Botones habilitados/deshabilitados:** Según estado del partido y rol del usuario
- **Lógica visible:** Tooltip explica por qué un botón está deshabilitado
- **Estados del partido:** Programado → En Juego → Finalizado

#### 4.5 Confirmación de resultado
- **Modal al finalizar:** Pide confirmación antes de cerrar el partido
- **Marcador visible:** Muestra resultado final antes de confirmar
- **Checkbox de verificación:** "He verificado que el resultado es correcto"
- **Seguridad:** Solo delegado o admin puede confirmar

---

## 2. 🎯 Onboarding

### OnboardingPage (`src/features/onboarding/pages/OnboardingPage.tsx`)

**Estado actual:** Saludo, 2 tarjetas de acción (crear/unirse), lista de ligas con tabs, búsqueda, dropdown de notificaciones y perfil.

**Mejoras propuestas:**

#### 5.1 Empty state mejorado
- **Guía paso a paso interactiva:** En lugar de solo texto, mostrar modal con 3 pasos
  - Paso 1: "¿Quieres crear una liga?" con botón directo
  - Paso 2: "¿Te han invitado?" con input para código
  - Paso 3: "¿Unirte a liga pública?" con lista de opciones
- **Progress indicator:** "Paso 1 de 3" visible
- **Navegación:** Botones "Atrás" y "Siguiente"

#### 5.2 Filtro por rol
- **Dropdown de filtrado:** "Filtrar por mi rol" con opciones Admin, Entrenador, Jugador, Delegado
- **Badge activo:** Cuando hay filtro, mostrar "Filtrando por: Entrenador" con opción de limpiar
- **Resultados en tiempo real:** La lista se actualiza al cambiar filtro

#### 5.3 Mini calendario de actividad
- **Calendario mensual pequeño:** Muestra el mes actual
- **Indicadores visuales:** Días con partidos tienen puntos de color
  - Verde: Partido de mi equipo
  - Azul: Partido de otras ligas
- **Tooltip al hover:** Muestra partidos del día sin hacer click
- **Click navega:** Lleva a la página de calendario en esa fecha

#### 5.4 Resumen de actividad semanal
- **Card después del saludo:** "Esta semana: 2 partidos, 1 entrenamiento"
- **Próximo evento:** "Mañana 18:00 vs Real Betis"
- **Tareas pendientes:** "3 convocatorias por confirmar"
- **Click navega:** Cada tarea lleva a su página correspondiente

#### 5.5 Botón de acciones rápidas flotante
- **Botón "+" flotante:** En posición inferior derecha, siempre visible
- **Menú desplegable:** Al hacer click muestra 3-4 opciones
  - Crear liga
  - Unirme a liga
  - Invitar equipo
- **Animación:** Los botones aparecen con efecto slide-up

#### 5.6 Tour guiado para primerizos
- **Overlay oscuro:** Con spotlight en el elemento activo
- **4 pasos:**
  1. Panel principal (highlight en header)
  2. Action cards (highlight en crear/unirse)
  3. Lista de ligas (highlight en grid)
  4. Acciones rápidas (highlight en botón +)
- **Persistencia:** Guarda en localStorage si el usuario completó el tour
- **Controles:** "Saltar", "Atrás", "Siguiente"

#### 5.7 Liga destacada
- **Card grande superior:** Antes de la grid de ligas, ocupa ancho completo
- **Criterio:** Liga favorita o más reciente activa
- **Contenido especial:**
  - Nombre más grande
  - Logo/escudo si existe
  - Badge "Tu liga principal"
  - Próximos partidos de esa liga en mini lista
  - Botón "Entrar" más prominente

---

### LeagueCard (`src/features/onboarding/components/LeagueCard.tsx`)

**Estado actual:** Nombre, temporada, badges de rol y estado, botón favorito, mi equipo, equipos totales, botón entrar/reactivar.

**Mejoras propuestas:**

#### 6.1 Logo/escudo de la liga
- **Espacio circular:** Para imagen del escudo
- **Fallback:** Si no hay logo, mostrar icono de trofeo o iniciales del nombre
- **Upload:** Para admin, opción de subir escudo personalizado

#### 6.2 Próximo partido
- **Mini sección:** Debajo de la información básica
- **Contenido:** Rival, fecha, si es local o visitante
- **Visual:** Icono de calendario pequeño

#### 6.3 Posición de mi equipo
- **Badge destacado:** "3º de 8" en color verde
- **Contexto:** Solo visible si el usuario tiene equipo en esa liga

#### 6.4 Badge de notificaciones
- **Contador rojo:** En esquina superior de la card
- **Número:** Cantidad de notificaciones no leídas de esa liga
- **Tope:** "9+" si hay más de 9

#### 6.5 Accesos directos en hover
- **3 iconos que aparecen:** Al pasar el mouse por la card
  - Escudo → Ver equipos
  - Calendario → Ver calendario
  - Trofeo → Ver clasificación
- **Click directo:** Navega a la página correspondiente

---

## 3. 📊 Páginas Secundarias

### LeaguePage (`src/features/league/pages/LeaguePage.tsx`)

**Estado actual:** Grid simple de cards con nombre, temporada, estado.

**Mejoras propuestas:**

#### 7.1 Vista de tabla alternativa
- **Toggle Grid/Tabla:** Botón para cambiar entre vistas
- **Columnas de tabla:** Nombre, Temporada, Estado, Número de equipos, Partidos jugados, Fecha de creación, Acciones
- **Ordenable:** Click en headers para ordenar

#### 7.2 Ordenamiento múltiple
- **Criterios:** Por nombre, fecha, estado, número de equipos
- **Dirección:** Ascendente o descendente
- **Indicador visual:** Flecha junto al nombre de columna activa

#### 7.3 Acciones masivas (solo admin)
- **Checkboxes:** Para seleccionar múltiples ligas
- **Barra de acciones:** Aparece cuando hay selección
- **Opciones:** Exportar seleccionadas, enviar notificación masiva, cambiar estado

#### 7.4 Filtros avanzados
- **Drawer lateral:** Se abre con botón "Filtros"
- **Opciones:**
  - Temporada (rango de años)
  - Estado (activa/finalizada)
  - Mi rol (múltiple selección)
  - Fecha de creación (date range)

#### 7.5 Liga activa destacada
- **Highlight visual:** Si hay una liga seleccionada en el contexto, se marca con borde de color
- **Posición:** Siempre aparece primera en la lista

---

### TeamPage (`src/features/team/pages/TeamPage.tsx`)

**Estado actual:** Grid de equipos con escudo placeholder, nombre, colores.

**Mejoras propuestas:**

#### 8.1 Escudos reales o generados
- **Imagen real:** Si el equipo tiene escudo subido
- **Generación automática:** Si no tiene, crear círculo con iniciales y colores del equipo
- **Upload:** Para admin/coach, botón para subir escudo

#### 8.2 Información expandible
- **Modal al hacer click:** Con toda la información del equipo
- **Contenido:**
  - Escudo grande + nombre
  - Estadio
  - Entrenador
  - Plantilla completa
  - Colores oficiales
  - Año de fundación

#### 8.3 Estadísticas del equipo
- **Métricas en modal:**
  - Posición en liga
  - Goles a favor y en contra
  - Partidos jugados
  - Victorias/Empates/Derrotas

#### 8.4 Acciones por rol
- **Admin:** Editar equipo, eliminar, transferir jugadores
- **Coach** (de su equipo): Ver convocatoria, editar alineación
- **Jugador** (de su equipo): Ver mi ficha, solicitar cambio de equipo

#### 8.5 Búsqueda y filtros
- **Input de búsqueda:** Filtra por nombre de equipo en tiempo real
- **Ordenar:** Por nombre, posición en liga, goles
- **Filtro:** Por categoría (Primera, Segunda, etc.)

---

### StatisticPage (`src/features/statistic/pages/StatisticPage.tsx`)

**Estado actual:** Tabla de jugadores ordenada por goles.

**Mejoras propuestas:**

#### 9.1 Múltiples categorías
- **Tabs horizontales:** Goles, Asistencias, Tarjetas, Porteros, Valoración
- **Contenido dinámico:** La tabla cambia según la tab seleccionada
- **Porteros:** Métricas específicas (paradas, clean sheets, goles encajados)

#### 9.2 Filtro por equipo
- **Dropdown:** "Todos los equipos" o seleccionar uno específico
- **Actualización:** La tabla se filtra en tiempo real

#### 9.3 Gráficas visuales
- **Top 5 barras horizontales:** Los líderes de cada categoría
- **Distribución:** Gráfico circular mostrando distribución por posición
- **Evolución:** Línea de tiempo de goles por jornada para el líder

#### 9.4 Exportar datos
- **Botón CSV:** Descarga archivo con estadísticas actuales
- **Opción PDF:** Genera informe con gráfica y tabla formateada
- **Selector de columnas:** Elegir qué datos incluir

#### 9.5 Comparativa de jugadores
- **Selección múltiple:** Checkbox para seleccionar hasta 3 jugadores
- **Tabla comparativa:** Stats de cada jugador lado a lado
- **Gráfico de radar:** 6 ejes (goles, asistencias, tarjetas, PJ, minutos, valoración)

#### 9.6 Estadísticas de equipo
- **Tab separada:** Para ver stats colectivas por equipo
- **Métricas:** Goles por partido, clean sheets, disciplina (tarjetas)

---

### CalendarPage ⚠️ **PENDIENTE - Actualmente "Próximamente"**

**Archivo:** `src/features/calendary/pages/CalendarPage.tsx`

**Implementación recomendada:**

#### 10.1 Vistas múltiples
- **Mes:** Calendario tradicional grid
- **Semana:** Vista semanal con horas en eje vertical
- **Lista:** Lista vertical cronológica de partidos

#### 10.2 Filtros
- **Por equipo:** Ver solo partidos de mi equipo
- **Por competición:** Filtrar por liga/torneo
- **Por estado:** Programados, en vivo, finalizados

#### 10.3 Click en partido
- **Modal de detalles:**
  - Equipos + marcador (si finalizado)
  - Fecha, hora, estadio
  - Convocatoria de ambos equipos
  - Eventos (goles, tarjetas, cambios)
  - Alineaciones (si disponibles)

#### 10.4 Añadir evento
- **Para admin/coach:** Botón "+" en header
- **Formulario:**
  - Selector de equipos
  - Fecha y hora
  - Estadio
  - Jornada/número de fecha

#### 10.5 Sincronización externa
- **Google Calendar:** Integración OAuth para exportar
- **iCal:** Descarga de archivo compatible
- **Outlook:** Exportación directa

#### 10.6 Recordatorios
- **Configuración:** Elegir cuándo recibir notificación (1h, 24h, 1 semana antes)
- **Múltiples canales:** Push notification, email, SMS

---

### UsersPage ⚠️ **PENDIENTE - Actualmente "Próximamente"**

**Archivo:** `src/features/users/pages/UsersPage.tsx`

**Implementación recomendada:**

#### 11.1 Tabla de usuarios
- **Columnas:** Usuario (avatar + nombre), Email, Rol, Equipos, Fecha registro, Acciones
- **Ordenable:** Por cualquier columna
- **Paginación:** Si hay muchos usuarios

#### 11.2 Gestión de roles
- **Dropdown por usuario:** Cambiar rol (Admin, Entrenador, Delegado, Jugador)
- **Confirmación:** Modal antes de aplicar cambio
- **Solo admin:** Esta funcionalidad restringida

#### 11.3 Invitar usuarios
- **Formulario modal:**
  - Emails (múltiple, separados por coma)
  - Rol a asignar
  - Equipo (opcional)
  - Mensaje personalizado
- **Tracking:** Ver estado de invitaciones (pendiente, aceptada)

#### 11.4 Bulk import
- **Upload CSV:** Arrastrar archivo o seleccionar
- **Preview:** Mostrar datos parseados antes de importar
- **Validación:** Mostrar errores (emails duplicados, roles inválidos)

#### 11.5 Estados de usuario
- **Badge visual:**
  - 🟢 Activo
  - ⚪ Inactivo
  - 🔴 Suspendido
  - 🟡 Pendiente de activación
- **Cambiar estado:** Modal para admin

#### 11.6 Perfiles expandibles
- **Click en usuario:** Abre modal con:
  - Información completa
  - Historial de ligas/equipos
  - Estadísticas personales
  - Actividad reciente

---

## 4. 🔐 Auth

### LoginPage (`src/features/auth/pages/LoginPage.tsx`)

**Estado actual:** Email, password, show/hide password, link a forgot-password.

**Mejoras propuestas:**

#### 12.1 Social login
- **Botones adicionales:** "Continuar con Google", "Continuar con Facebook"
- **Separador visual:** "O continúa con" entre formulario y botones sociales
- **OAuth flow:** Redirect automático para autenticación

#### 12.2 Recordarme
- **Checkbox:** "Recordarme en este dispositivo"
- **Persistencia:** Token de 30 días vs 24 horas
- **Seguridad:** No ofrecer en dispositivos públicos

#### 12.3 Validación en tiempo real
- **Mensajes mientras escribe:** Error de formato aparece después de 1 segundo
- **Debounce:** No mostrar error inmediatamente, esperar a que termine de escribir
- **Visual:** Borde rojo + texto explicativo

#### 12.4 Link a términos
- **Texto discreto:** Debajo del botón de login
- **Enlaces:** Términos de servicio y Política de privacidad
- **Legal:** Requerido en algunas jurisdicciones

---

### RegisterPage (`src/features/auth/pages/RegisterPage.tsx`)

**Estado actual:** Nombre, email, password, confirmar password, checkbox términos.

**Mejoras propuestas:**

#### 13.1 Medidor de fortaleza de contraseña
- **Barra visual:** 4 segmentos que se llenan
- **Colores:** Rojo → Naranja → Amarillo → Verde
- **Texto:** "Débil", "Media", "Fuerte", "Muy fuerte"

#### 13.2 Requisitos visibles
- **Lista de checkboxes:**
  - Al menos 8 caracteres
  - Una mayúscula
  - Una minúscula
  - Un número
- **Se marcan en verde:** Cuando se cumplen en tiempo real

#### 13.3 Validación de email
- **Check de disponibilidad:** Verifica si email ya está registrado
- **Feedback inmediato:** "Email disponible" o "Este email ya está en uso"
- **Debounce:** Espera 1 segundo después de dejar de escribir

#### 13.4 Teléfono opcional
- **Campo adicional:** Para notificaciones SMS futuras
- **Formato internacional:** Placeholder con ejemplo "+34 612 345 678"
- **No obligatorio:** Puede dejarse vacío

#### 13.5 Fecha de nacimiento
- **Input de fecha:** Date picker estándar
- **Validación de edad:** Debe ser mayor de 14 o 18 años
- **Uso futuro:** Para categorías por edad

---

## 5. 🌐 Public Dashboard

**Archivo:** `src/features/main/pages/PublicDashboardPage.tsx`

**Estado actual:** Hero section, features grid, resultados recientes, próximos partidos, clasificación, CTA final.

**Mejoras propuestas:**

#### 14.1 Testimonios
- **Cards con quotes:** De usuarios reales (entrenadores, admins, jugadores)
- **Avatar + nombre + rol:** "Carlos M., Entrenador, Atletico Villa"
- **Carrusel:** Si hay más de 3 testimonios

#### 14.2 Demo interactiva
- **Tour sin registro:** Screenshots interactivos de la plataforma
- **Pasos guiados:** Dashboard, gestión de equipos, resultados en vivo
- **CTA final:** "¿Listo para empezar?" con botón de registro

#### 14.3 Precios/planes
- **3 tiers:** Gratis, Pro, Enterprise
- **Comparativa visual:** Features marcadas con check
- **Toggle:** Mensual vs Anual (con descuento)

#### 14.4 Estadísticas de plataforma
- **Números grandes:** Usuarios, ligas, partidos, goles
- **Animación:** Count-up effect al hacer scroll
- **Actualización:** Datos reales o aproximados

#### 14.5 Logos de partners
- **Grid de logos:** Ligas o equipos que usan la plataforma
- **Título:** "Confían en GoalApp"
- **Social proof:** Validación externa

#### 14.6 FAQ section
- **Accordion:** Preguntas frecuentes expandibles
- **Posición:** Antes del footer
- **Contenido:** Precios, funcionalidades, soporte

#### 14.7 Chat en vivo
- **Widget flotante:** En esquina inferior derecha
- **Estado:** "En línea" o "Déjanos un mensaje"
- **Horario:** Visible solo en horario de soporte

---

## 6. 🧭 Navegación

### Nav (`src/components/Nav.tsx`)

**Estado actual:** Logo, selector de liga, nav items, notificaciones, perfil dropdown.

**Mejoras propuestas:**

#### 15.1 Breadcrumbs
- **Ruta actual:** "Liga Municipal > Equipos > Atletico Villa"
- **Posición:** Debajo del header principal
- **Separador:** "/" entre items
- **No clicable:** El último item (página actual)

#### 15.2 Búsqueda global
- **Icono de lupa:** En header
- **Modal al hacer click:** Buscador que abarca toda la pantalla
- **Resultados por sección:** Ligas, Equipos, Jugadores
- **Atajo de teclado:** Cmd+K o Ctrl+K abre el buscador

#### 15.3 Notificaciones con preview
- **Hover en icono:** Muestra últimas 2-3 notificaciones
- **Tooltip:** Con título de cada notificación
- **Click:** Navega a página completa de notificaciones

#### 15.4 Atajos de teclado
- **Combinaciones:**
  - G + D → Dashboard
  - G + C → Calendario
  - G + T → Equipos
  - / → Enfocar buscador
- **Visual:** Modal pequeño muestra atajos disponibles

#### 15.5 Estado de conexión
- **Indicador visual:** Punto verde/rojo junto al avatar
- **Verde:** Conectado a la API
- **Rojo:** Sin conexión, mostrando toast "Reconectando..."

---

## 7. 📊 Prioridades de Implementación

| Prioridad | Mejora | Archivo(s) | Impacto | Esfuerzo estimado |
|-----------|--------|------------|---------|-------------------|
| 🔴 ALTA | PlayerDashboard con datos reales | `roles/PlayerDashboard.tsx` | Crítico | 2 días |
| 🔴 ALTA | DelegateDashboard con datos reales | `roles/DelegateDashboard.tsx` | Crítico | 2 días |
| 🔴 ALTA | CalendarPage funcional | `CalendarPage.tsx` | Alto | 4 días |
| 🔴 ALTA | UsersPage funcional | `UsersPage.tsx` | Alto | 3 días |
| 🟡 MEDIA | Notificaciones dropdown funcional | `Nav.tsx`, `notificationsApi.ts` | Medio | 1 día |
| 🟡 MEDIA | Estadísticas personales | `PlayerDashboard.tsx` | Medio | 1 día |
| 🟡 MEDIA | Empty states mejorados | `OnboardingPage.tsx` | Medio | 0.5 días |
| 🟢 BAJA | Gráficas y visualizaciones | Múltiples | Bajo | 2 días |
| 🟢 BAJA | Atajos de teclado | `Nav.tsx` | Bajo | 0.5 días |

### Total estimado: **16 días de desarrollo**

---

## Resumen de Archivos a Modificar

### Dashboards
- `src/features/main/components/dashboard/roles/AdminDashboard.tsx`
- `src/features/main/components/dashboard/roles/CoachDashboard.tsx`
- `src/features/main/components/dashboard/roles/PlayerDashboard.tsx` ⚠️
- `src/features/main/components/dashboard/roles/DelegateDashboard.tsx` ⚠️

### Onboarding
- `src/features/onboarding/pages/OnboardingPage.tsx`
- `src/features/onboarding/components/LeagueCard.tsx`

### Páginas Secundarias
- `src/features/league/pages/LeaguePage.tsx`
- `src/features/team/pages/TeamPage.tsx`
- `src/features/statistic/pages/StatisticPage.tsx`
- `src/features/calendary/pages/CalendarPage.tsx` ⚠️ PENDIENTE
- `src/features/users/pages/UsersPage.tsx` ⚠️ PENDIENTE

### Auth
- `src/features/auth/pages/LoginPage.tsx`
- `src/features/auth/pages/RegisterPage.tsx`

### Público
- `src/features/main/pages/PublicDashboardPage.tsx`

### Navegación
- `src/components/Nav.tsx`

---

## Notas Adicionales

### Componentes Nuevos a Crear

1. **ActivityChart.tsx** - Gráficas de actividad para AdminDashboard
2. **PendingNotificationsWidget.tsx** - Widget de notificaciones pendientes
3. **QuickActionButton.tsx** - Botones de acceso rápido
4. **ConfigurationProgress.tsx** - Progress bar de configuración
5. **NextMatchHero.tsx** - Card destacada de próximo partido (Coach)
6. **SquadStatus.tsx** - Estado de la plantilla
7. **QuickCallupButton.tsx** - Botón rápido de convocatoria
8. **RecommendedFormation.tsx** - Formación recomendada
9. **MyNextMatch.tsx** - Mi próximo partido (Player)
10. **PlayerStatusSelector.tsx** - Selector de estado personal
11. **PlayerMatchHistory.tsx** - Historial de partidos
12. **LeagueComparison.tsx** - Comparativa con la liga
13. **PreMatchChecklist.tsx** - Checklist pre-partido (Delegate)
14. **MatchEventTimeline.tsx** - Timeline de eventos
15. **MatchTimer.tsx** - Contador de tiempo del partido
16. **ConfirmResultModal.tsx** - Confirmación de resultado
17. **InteractiveGuideModal.tsx** - Guía interactiva (Onboarding)
18. **MiniCalendarWidget.tsx** - Mini calendario
19. **WeeklyActivitySummary.tsx** - Resumen semanal
20. **OnboardingTour.tsx** - Tour guiado
21. **TeamDetailModal.tsx** - Modal de detalles de equipo
22. **TeamSearch.tsx** - Búsqueda de equipos
23. **StatsCharts.tsx** - Gráficas de estadísticas
24. **PlayerComparison.tsx** - Comparativa de jugadores
25. **MatchDetailModal.tsx** - Detalles de partido (Calendar)
26. **CreateMatchModal.tsx** - Crear partido
27. **ExportCalendar.tsx** - Exportar calendario
28. **MatchReminders.tsx** - Recordatorios de partidos
29. **UsersTable.tsx** - Tabla de usuarios
30. **RoleSelector.tsx** - Selector de rol
31. **InviteUsersModal.tsx** - Invitar usuarios
32. **BulkImportUsers.tsx** - Importación masiva
33. **UserProfileModal.tsx** - Perfil de usuario
34. **PasswordStrength.tsx** - Medidor de contraseña
35. **PasswordRequirements.tsx** - Requisitos de contraseña
36. **TestimonialsSection.tsx** - Testimonios (Public)
37. **InteractiveDemo.tsx** - Demo interactiva
38. **PricingSection.tsx** - Precios/planes
39. **PlatformStats.tsx** - Estadísticas de plataforma
40. **PartnersSection.tsx** - Logos de partners
41. **FAQSection.tsx** - Preguntas frecuentes
42. **LiveChatWidget.tsx** - Chat en vivo
43. **Breadcrumbs.tsx** - Breadcrumbs (Nav)
44. **GlobalSearch.tsx** - Búsqueda global
45. **ConnectionStatus.tsx** - Estado de conexión

### Endpoints de API Necesarios

Los siguientes endpoints del backend pueden ser necesarios para implementar estas mejoras:

- `GET /api/v1/ligas/{id}/estadisticas/jornada` - Goles por jornada
- `GET /api/v1/partidos/proximo?equipoId={id}` - Próximo partido
- `GET /api/v1/equipos/{id}/jugadores/estado` - Estado de jugadores
- `GET /api/v1/jugadores/{id}/estadisticas?liga={id}` - Stats personales
- `GET /api/v1/partidos/{id}/checklist` - Checklist pre-partido
- `GET /api/v1/partidos/{id}/eventos` - Eventos del partido
- `PUT /api/v1/jugadores/{id}/estado` - Actualizar estado jugador
- `POST /api/v1/convocatorias` - Crear convocatoria
- `GET /api/v1/usuarios/{id}/actividad/semanal` - Actividad semanal
- `GET /api/v1/buscar?q={query}` - Búsqueda global
- `GET /api/v1/health` - Health check para conexión

---

**Documento generado:** 2026-04-18  
**Autor:** Claude Code (asistente de desarrollo)  
**Versión:** 1.0
