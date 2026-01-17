# Liga Amateur App

## 1. Descripción

Aplicación multiplataforma (Android, iOS y Web) para la gestión de ligas de fútbol amateur.  
Permite crear ligas, equipos y jugadores, generar calendarios automáticos, introducir resultados y consultar clasificaciones y estadísticas en tiempo real.

El proyecto está orientado a grupos de amigos, asociaciones o ligas locales que buscan una herramienta intuitiva para administrar sus competiciones sin depender de sistemas externos.

**Características principales:**

- Gestión de ligas, equipos y jugadores
    
- Registro de partidos y eventos (goles, tarjetas, cambios, MVP)
    
- Formaciones y alineaciones tácticas
    
- Clasificaciones y estadísticas automáticas
    
- Roles diferenciados: administrador, entrenador, jugador, delegado de campo y espectador
    
- Notificaciones push para partidos y resultados
    

---

## 2. Tecnologías

**Frontend:**

- React Native + Expo
    
- Tailwind CSS
    
- React Navigation
    

**Backend:**

- Python + FastAPI
    
- API REST para comunicación con el frontend
    
- Autenticación y autorización por roles
    

**Base de datos:**

- PostgreSQL o MySQL
    
- Modelo relacional normalizado con tablas: usuarios, roles, jugadores, equipos, ligas, partidos, eventos, formaciones, alineaciones y notificaciones
    

**Hosting:**

- Backend: Railway / Render
    
- App: exportación a Android/iOS/Web
    

---

## 3. Estructura del repositorio

```
├── backend/
│   ├── app/                 # Código del backend (FastAPI)
│   ├── database/            # Migraciones y scripts SQL
│   ├── models/              # Modelos de datos
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes reutilizables
│   │   ├── screens/         # Pantallas principales
│   │   ├── navigation/      # Rutas y navegación
│   │   └── assets/          # Imágenes y recursos
│   └── App.js
│
└── README.md
```

---

## 4. Roles de usuario

- **Administrador (Admin):** gestión global de ligas, equipos y usuarios
    
- **Entrenador (Coach):** gestión del equipo y alineaciones
    
- **Delegado de campo (Delegate):** registro de eventos en los partidos
    
- **Jugador (Player):** consulta de información y estadísticas propias
    
- **Espectador (Viewer):** consulta de información pública
    

---
---

## 5. Documentación

- **Modelo conceptual:** `docs/modelo_datos_conceptual.md`
    
- **Modelo SQL y scripts:** `docs/modelo_datos_sql.md`
    

---

## 6. Contribución

- Mantener la estructura de carpetas
    
- Seguir las convenciones de nombres
    
- Documentar nuevas funcionalidades en `docs/`
    
- Usar commits claros y descriptivos
    

---

## 7. Escalabilidad y mejoras futuras

- Añadir panel web de administración completo
    
- IA para predecir “jugador de la jornada”
    
- Exportación de estadísticas y clasificaciones a PDF
    
- Integración con notificaciones push avanzadas