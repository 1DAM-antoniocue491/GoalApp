# app/main.py
"""
Punto de entrada principal de la aplicación FastAPI.
Configura la aplicación, middlewares, routers y eventos de ciclo de vida.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database.connection import engine, Base

# Importar todos los routers
from .api.routers import (
    auth,
    usuarios,
    roles,
    equipos,
    jugadores,
    ligas,
    partidos,
    eventos,
    formaciones,
    notificaciones
)


# ============================================================
# EVENTOS DE CICLO DE VIDA
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    Se ejecuta al inicio y al cierre del servidor.
    """
    # Startup: Crear tablas si no existen
    print("🚀 Iniciando aplicación...")
    print(f"📊 Conectando a base de datos: {settings.DATABASE_URL.split('@')[1]}")
    
    # Crear todas las tablas definidas en los modelos
    # NOTA: En producción, usar Alembic en lugar de esto
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos verificadas")
    
    yield
    
    # Shutdown: Cerrar conexiones
    print("🛑 Cerrando aplicación...")
    engine.dispose()
    print("✅ Conexiones de base de datos cerradas")


# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="API REST para gestión de ligas de fútbol amateur",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    lifespan=lifespan
)


# ============================================================
# MIDDLEWARE DE CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),  # Convierte string a lista
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REGISTRO DE ROUTERS
# ============================================================

# Autenticación
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Autenticación"]
)

# Usuarios y roles
app.include_router(
    usuarios.router,
    prefix="/api/v1",
    tags=["Usuarios"]
)

app.include_router(
    roles.router,
    prefix="/api/v1",
    tags=["Roles"]
)

# Ligas, equipos y jugadores
app.include_router(
    ligas.router,
    prefix="/api/v1",
    tags=["Ligas"]
)

app.include_router(
    equipos.router,
    prefix="/api/v1",
    tags=["Equipos"]
)

app.include_router(
    jugadores.router,
    prefix="/api/v1",
    tags=["Jugadores"]
)

# Partidos y eventos
app.include_router(
    partidos.router,
    prefix="/api/v1",
    tags=["Partidos"]
)

app.include_router(
    eventos.router,
    prefix="/api/v1",
    tags=["Eventos"]
)

# Formaciones y notificaciones
app.include_router(
    formaciones.router,
    prefix="/api/v1",
    tags=["Formaciones"]
)

app.include_router(
    notificaciones.router,
    prefix="/api/v1",
    tags=["Notificaciones"]
)


# ============================================================
# ENDPOINTS DE SALUD Y RAÍZ
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    """
    return {
        "mensaje": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.API_VERSION,
        "entorno": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint para verificar el estado de salud de la API.
    Útil para monitoring y balanceadores de carga.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


# ============================================================
# PUNTO DE ENTRADA PARA EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  {settings.APP_NAME:^55}  ║
    ║  Version: {settings.API_VERSION:^48}  ║
    ║  Entorno: {settings.ENVIRONMENT:^48}  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
