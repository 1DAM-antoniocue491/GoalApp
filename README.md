# ⚽ GoalApp - Sistema Integral de Gestión de Ligas de Fútbol Amateur

GoalApp es una plataforma completa diseñada para la administración de competiciones de fútbol amateur, permitiendo una gestión profesional de ligas, equipos, jugadores y la operativa de partidos en tiempo real.

El proyecto se divide en tres componentes principales que trabajan de forma coordinada para ofrecer una experiencia fluida tanto en web como en dispositivos móviles.

---

## 📚 Documentación Oficial

Para acceder a la guía técnica completa, manuales de usuario y arquitectura del sistema, visita la documentación oficial en GitBook:

👉 **[Documentación de GoalApp](https://tonyalg.gitbook.io/goalapp-doc/)**

---

## 🌐 Repositorios del Ecosistema

Para acceder al código fuente de cada módulo, utiliza los siguientes enlaces:

- ⚙️ **[GoalApp Backend](https://github.com/1DAM-antoniocue491/GoalApp_Backend.git)** $\rightarrow$ API REST, Lógica de Negocio y Base de Datos.
- 💻 **[GoalApp Frontend Web](https://github.com/1DAM-antoniocue491/GoalApp_Frontend_Web.git)** $\rightarrow$ Panel de Administración y Consulta (React 19).
- 📱 **[GoalApp Frontend Móvil](https://github.com/1DAM-antoniocue491/GoalApp_Frontend_Movil.git)** $\rightarrow$ Aplicación Nativa para Usuarios y Delegados (Expo).

---

## 🚀 Resumen Técnico del Ecosistema

| Componente | Stack Principal | Base de Datos / Almacenamiento | Despliegue | Características Clave |
| :--- | :--- | :--- | :--- | :--- |
| **API (Backend)** | FastAPI / Python 3.13 | PostgreSQL (Supabase) | Render | RBAC, Gestión de Ligas, Estadísticas |
| **Web (Frontend)** | React 19 / Vite / TW4 | JWT / LocalStorage | Firebase | Feature-based Arch, Refresh Token Flow |
| **Mobile (App)** | Expo 54 / NativeWind | Expo Secure Store | App/Play Store | Exponential Backoff, Expo Router |

---

## 🛠️ Detalles de los Componentes

### ⚙️ Backend (API REST)
El núcleo del sistema, construido con **FastAPI** y una arquitectura por capas (Routers $\rightarrow$ Services $\rightarrow$ Models).
- **Funcionalidades Core**: Gestión de ligas, equipos, jornadas, partidos, alineaciones y convocatorias.
- **Operativa de Juego**: Registro de eventos en vivo (goles, tarjetas, MVP) y cálculo de estadísticas avanzadas.
- **Seguridad**: Sistema de Roles (Admin, Coach, Delegate, Player), autenticación JWT y gestión de invitaciones mediante códigos.
- **Infraestructura**: Base de datos PostgreSQL en Supabase y almacenamiento de imágenes mediante Supabase Storage.

### 💻 Frontend Web
Interfaz de administración y consulta optimizada para escritorio, desarrollada con **React 19**.
- **Arquitectura**: Organización basada en **Features**, separando la lógica por dominios funcionales para garantizar la escalabilidad.
- **Sincronización**: Implementación de interceptores de Axios para la gestión automática de sesiones y el flujo de *Refresh Tokens*.
- **Estilos**: Interfaz moderna y responsiva utilizando **Tailwind CSS 4**.

### 📱 Frontend Móvil
Aplicación nativa construida con **Expo SDK 54**, enfocada en la resiliencia y la movilidad.
- **Navegación**: Implementación de **Expo Router** para una gestión de rutas eficiente basada en archivos.
- **Resiliencia de Red**: Sistema de reintentos con **Backoff Exponencial**, asegurando que la app siga funcionando en condiciones de conectividad inestable.
- **Seguridad Móvil**: Uso de `expo-secure-store` para el almacenamiento cifrado de credenciales y tokens.

---

## 🎯 Objetivos del Proyecto
1. **Digitalizar la gestión deportiva**: Eliminar la dependencia de papel y hojas de cálculo en ligas amateur.
2. **Proporcionar datos en tiempo real**: Permitir que jugadores y entrenadores sigan los eventos de los partidos al instante.
3. **Garantizar la integridad de los datos**: Implementar un sistema robusto de permisos (RBAC) para que solo los usuarios autorizados modifiquen la información.
4. **Ofrecer accesibilidad total**: Disponibilidad multiplataforma mediante una API unificada.
