# Datos de Prueba - GoalApp

Este documento contiene un resumen de los datos de prueba insertados en la base de datos de GoalApp.

## Conexión a la Base de Datos

| Parámetro | Valor |
|-----------|-------|
| Host | sql7.freesqldatabase.com |
| Usuario | sql7822417 |
| Base de datos | sql7822417 |

---

## Estructura de Tablas

La base de datos contiene **15 tablas**:

| Tabla | Descripción |
|-------|-------------|
| `usuarios` | Usuarios del sistema |
| `roles` | Roles disponibles (admin, coach, player, viewer, delegate) |
| `usuario_rol` | Asignación de roles a usuarios |
| `ligas` | Ligas de fútbol |
| `liga_configuracion` | Configuración de cada liga |
| `usuario_sigue_liga` | Relación usuarios-ligas que siguen |
| `equipos` | Equipos de fútbol |
| `jugadores` | Jugadores de cada equipo |
| `partidos` | Partidos programados/jugados |
| `evento_partido` | Eventos de cada partido (goles, tarjetas, etc.) |
| `alineacion_partido` | Alineaciones de jugadores en partidos |
| `convocatoria_partido` | Convocatorias de jugadores para partidos |
| `posicion_formacion` | Posiciones tácticas disponibles |
| `notificaciones` | Notificaciones a usuarios |
| `tokens_recuperacion` | Tokens para recuperación de contraseña |

---

## Datos Insertados

### Resumen

| Entidad | Cantidad |
|---------|----------|
| Usuarios | 25 |
| Roles | 5 |
| Asignaciones de rol | 25 |
| Ligas | 2 |
| Posiciones tácticas | 10 |
| Configuraciones de liga | 2 |
| Seguimientos de liga | 15 |
| Equipos | 6 |
| Jugadores | 15 |
| Partidos | 6 |
| Eventos de partido | 10 |
| Convocatorias | 9 |
| Notificaciones | 5 |

---

### Usuarios de Prueba

#### Administradores
| Email | Contraseña | Nombre |
|-------|------------|--------|
| admin@goalapp.com | admin123 | Carlos Admin |
| maria.admin@goalapp.com | admin123 | María Admin |

#### Entrenadores (Coaches)
| Email | Contraseña | Nombre |
|-------|------------|--------|
| pedro.coach@goalapp.com | coach123 | Pedro García |
| luis.coach@goalapp.com | coach123 | Luis Fernández |
| ana.coach@goalapp.com | coach123 | Ana Martínez |
| roberto.coach@goalapp.com | coach123 | Roberto Díaz |

#### Delegados
| Email | Contraseña | Nombre |
|-------|------------|--------|
| fernando.del@goalapp.com | del123 | Fernando López |
| carmen.del@goalapp.com | del123 | Carmen Ruiz |
| javier.del@goalapp.com | del123 | Javier Torres |
| laura.del@goalapp.com | del123 | Laura Sánchez |

#### Jugadores
| Email | Contraseña | Nombre |
|-------|------------|--------|
| juan.player@goalapp.com | player123 | Juan Rodríguez |
| miguel.player@goalapp.com | player123 | Miguel Pérez |
| david.player@goalapp.com | player123 | David Moreno |
| sergio.player@goalapp.com | player123 | Sergio Navarro |
| pablo.player@goalapp.com | player123 | Pablo Molina |
| daniel.player@goalapp.com | player123 | Daniel Ortega |
| alex.player@goalapp.com | player123 | Alejandro Serrano |
| jorge.player@goalapp.com | player123 | Jorge Herrero |
| andres.player@goalapp.com | player123 | Andrés Castro |
| raul.player@goalapp.com | player123 | Raúl Medina |
| ivan.player@goalapp.com | player123 | Iván Rubio |
| marcos.player@goalapp.com | player123 | Marcos Blanco |
| hugo.player@goalapp.com | player123 | Hugo Delgado |
| adrian.player@goalapp.com | player123 | Adrián Vera |
| alvaro.player@goalapp.com | player123 | Álvaro Gil |

---

### Ligas

| ID | Nombre | Temporada | Estado |
|----|--------|-----------|--------|
| 1 | Liga Municipal de Fútbol | 2025-2026 | Activa |
| 2 | Torneo Verano | 2025 | Activa |

---

### Equipos

#### Liga Municipal de Fútbol
| Equipo | Colores | Entrenador | Delegado |
|--------|---------|------------|----------|
| Atlético Villa | Rojo/Blanco | Pedro García | Fernando López |
| FC Porteño | Azul/Amarillo | Luis Fernández | Carmen Ruiz |
| Deportivo Central | Verde/Blanco | Ana Martínez | Javier Torres |
| Unión FC | Negro/Blanco | Roberto Díaz | Laura Sánchez |

#### Torneo Verano
| Equipo | Colores | Entrenador | Delegado |
|--------|---------|------------|----------|
| Real Verano | Naranja/Negro | Pedro García | Fernando López |
| CD Sol | Amarillo/Azul | Luis Fernández | Carmen Ruiz |

---

### Jugadores por Equipo

#### Atlético Villa
| Jugador | Posición | Dorsal |
|---------|----------|--------|
| Juan Rodríguez | Portero | 1 |
| Miguel Pérez | Defensa Central | 4 |
| David Moreno | Delantero Centro | 9 |

#### FC Porteño
| Jugador | Posición | Dorsal |
|---------|----------|--------|
| Sergio Navarro | Lateral Derecho | 2 |
| Pablo Molina | Mediocentro | 8 |
| Daniel Ortega | Extremo Izquierdo | 11 |

#### Deportivo Central
| Jugador | Posición | Dorsal |
|---------|----------|--------|
| Alejandro Serrano | Portero | 13 |
| Jorge Herrero | Defensa Central | 5 |
| Andrés Castro | Mediocentro Ofensivo | 10 |

#### Unión FC
| Jugador | Posición | Dorsal |
|---------|----------|--------|
| Raúl Medina | Lateral Izquierdo | 3 |
| Iván Rubio | Mediocentro Defensivo | 6 |
| Marcos Blanco | Extremo Derecho | 7 |

#### Real Verano
| Jugador | Posición | Dorsal |
|---------|----------|--------|
| Hugo Delgado | Portero | 1 |
| Adrián Vera | Delantero Centro | 9 |

#### CD Sol
| Jugador | Posición | Dorsal |
|---------|----------|--------|
| Álvaro Gil | Mediocentro | 8 |

---

### Partidos

#### Liga Municipal de Fútbol
| ID | Local | Visitante | Fecha | Estado | Resultado |
|----|-------|-----------|-------|--------|-----------|
| 1 | Atlético Villa | FC Porteño | 2025-04-01 17:00 | Finalizado | 2-1 |
| 2 | Deportivo Central | Unión FC | 2025-04-08 17:00 | Finalizado | 0-0 |
| 3 | Atlético Villa | Deportivo Central | 2025-04-15 17:00 | Programado | - |
| 4 | FC Porteño | Unión FC | 2025-04-22 17:00 | Programado | - |

#### Torneo Verano
| ID | Local | Visitante | Fecha | Estado | Resultado |
|----|-------|-----------|-------|--------|-----------|
| 5 | Real Verano | CD Sol | 2025-04-05 19:00 | Finalizado | 3-2 |
| 6 | Real Verano | CD Sol | 2025-04-12 19:00 | Programado | - |

---

### Eventos de Partido

| Partido | Jugador | Evento | Minuto |
|---------|---------|--------|--------|
| 1 (Atlético Villa 2-1 FC Porteño) | Juan Rodríguez | Gol | 23' |
| 1 (Atlético Villa 2-1 FC Porteño) | Juan Rodríguez | Gol | 67' |
| 1 (Atlético Villa 2-1 FC Porteño) | Sergio Navarro | Gol | 78' |
| 1 (Atlético Villa 2-1 FC Porteño) | Miguel Pérez | Tarjeta Amarilla | 35' |
| 5 (Real Verano 3-2 CD Sol) | Hugo Delgado | Gol | 15' |
| 5 (Real Verano 3-2 CD Sol) | Hugo Delgado | Gol | 30' |
| 5 (Real Verano 3-2 CD Sol) | Hugo Delgado | Gol | 55' |
| 5 (Real Verano 3-2 CD Sol) | Adrián Vera | Gol | 20' |
| 5 (Real Verano 3-2 CD Sol) | Adrián Vera | Gol | 75' |
| 5 (Real Verano 3-2 CD Sol) | Hugo Delgado | Tarjeta Roja | 60' |

---

### Posiciones Tácticas

| ID | Posición | Descripción |
|----|----------|-------------|
| 1 | Portero | Guardameta |
| 2 | Defensa Central | Defensa central |
| 3 | Lateral Izquierdo | Defensa lateral izquierdo |
| 4 | Lateral Derecho | Defensa lateral derecho |
| 5 | Mediocentro Defensivo | Pivote |
| 6 | Mediocentro | Centrocampista |
| 7 | Mediocentro Ofensivo | Mediapunta |
| 8 | Extremo Izquierdo | Extremo por banda izquierda |
| 9 | Extremo Derecho | Extremo por banda derecha |
| 10 | Delantero Centro | Delantero |

---

### Roles del Sistema

| ID | Rol | Descripción |
|----|-----|-------------|
| 1 | admin | Administrador del sistema con acceso total |
| 2 | coach | Entrenador de equipo |
| 3 | player | Jugador |
| 4 | viewer | Visualizador de información pública |
| 5 | delegate | Delegado de equipo |

---

## Notas

- Las contraseñas están hasheadas con SHA-256 para propósitos de prueba
- Los partidos finalizados tienen resultados registrados
- Los partidos programados tienen fecha futura sin resultado
- Las notificaciones son ejemplos de mensajes del sistema