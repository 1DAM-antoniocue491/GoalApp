from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================

# Cambiar a credenciales reales
DATABASE_URL = "mysql+pymysql://usuario:password@localhost:3306/futbol_app"

# Al pasar a desarrollo, echo=False
# Muestra consultas SQL en consola
engine = create_engine(
    DATABASE_URL,
    echo=True,  
    pool_pre_ping=True
)

# Crea la fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()
