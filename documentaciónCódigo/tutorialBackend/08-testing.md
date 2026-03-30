# Testing

## Configuración

### Instalar dependencias

```bash
pip install pytest pytest-cov httpx
```

### Estructura

```
backend/
├── app/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Configuración y fixtures
│   ├── test_auth.py          # Tests de autenticación
│   ├── test_usuarios.py      # Tests de usuarios
│   └── test_ligas.py         # Tests de ligas
├── pytest.ini
└── requirements.txt
```

## Fixtures

### `conftest.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.main import app
from app.api.dependencies import get_db

# Base de datos en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Crea una base de datos en memoria para cada test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Cliente de prueba para peticiones HTTP."""
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides = {}


@pytest.fixture
def usuario_ejemplo(db):
    """Crea un usuario de prueba."""
    from app.models.usuario import Usuario
    from app.api.services.usuario_service import hash_password

    usuario = Usuario(
        nombre="Usuario Test",
        email="test@email.com",
        contraseña_hash=hash_password("password123")
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def token_usuario(client, usuario_ejemplo):
    """Obtiene un token JWT para el usuario de prueba."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_ejemplo.email,
            "password": "password123"
        }
    )
    return response.json()["access_token"]
```

## Tests de Servicios

```python
# tests/test_usuario_service.py
import pytest
from app.api.services.usuario_service import (
    crear_usuario,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    autenticar_usuario
)
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


def test_crear_usuario(db):
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )

    usuario = crear_usuario(db, datos)

    assert usuario.id_usuario is not None
    assert usuario.nombre == "Juan García"
    assert usuario.email == "juan@email.com"
    assert usuario.contraseña_hash != "mi_contraseña"


def test_crear_usuario_email_duplicado(db):
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )

    crear_usuario(db, datos)

    with pytest.raises(ValueError, match="email ya está registrado"):
        crear_usuario(db, datos)


def test_obtener_usuario_por_id(db):
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    usuario_creado = crear_usuario(db, datos)

    usuario_encontrado = obtener_usuario_por_id(db, usuario_creado.id_usuario)

    assert usuario_encontrado is not None
    assert usuario_encontrado.email == "juan@email.com"


def test_actualizar_usuario(db):
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    usuario = crear_usuario(db, datos)

    datos_actualizacion = UsuarioUpdate(nombre="Juan Carlos")
    usuario_actualizado = actualizar_usuario(db, usuario.id_usuario, datos_actualizacion)

    assert usuario_actualizado.nombre == "Juan Carlos"


def test_autenticar_usuario_correcto(db):
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    crear_usuario(db, datos)

    usuario = autenticar_usuario(db, "juan@email.com", "mi_contraseña")

    assert usuario is not None
    assert usuario.email == "juan@email.com"


def test_autenticar_usuario_password_incorrecta(db):
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    crear_usuario(db, datos)

    usuario = autenticar_usuario(db, "juan@email.com", "incorrecta")

    assert usuario is None
```

## Tests de API

```python
# tests/test_auth.py
import pytest


def test_login_correcto(client, usuario_ejemplo):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_ejemplo.email,
            "password": "password123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_password_incorrecta(client, usuario_ejemplo):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_ejemplo.email,
            "password": "incorrecta"
        }
    )

    assert response.status_code == 401


def test_obtener_perfil_sin_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_obtener_perfil_con_token(client, token_usuario):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_usuario}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
```

```python
# tests/test_usuarios.py


def test_crear_usuario(client):
    response = client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Nuevo Usuario",
            "email": "nuevo@email.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nuevo Usuario"
    assert "password" not in data


def test_crear_usuario_email_duplicado(client):
    client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Usuario 1",
            "email": "test@email.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Usuario 2",
            "email": "test@email.com",
            "password": "password456"
        }
    )

    assert response.status_code == 400


def test_listar_usuarios(client):
    for i in range(3):
        client.post(
            "/api/v1/usuarios/",
            json={
                "nombre": f"Usuario {i}",
                "email": f"usuario{i}@email.com",
                "password": "password123"
            }
        )

    response = client.get("/api/v1/usuarios/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_obtener_usuario_por_id(client):
    crear = client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Usuario Test",
            "email": "test@email.com",
            "password": "password123"
        }
    )
    usuario_id = crear.json()["id_usuario"]

    response = client.get(f"/api/v1/usuarios/{usuario_id}")

    assert response.status_code == 200
    assert response.json()["id_usuario"] == usuario_id


def test_obtener_usuario_no_existente(client):
    response = client.get("/api/v1/usuarios/999")
    assert response.status_code == 404
```

## Tests con Roles

```python
# tests/test_roles.py
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol


@pytest.fixture
def usuario_admin(db, usuario_ejemplo):
    """Crea un usuario con rol admin."""
    rol = Rol(nombre="admin", descripcion="Administrador")
    db.add(rol)
    db.commit()
    db.refresh(rol)

    usuario_rol = UsuarioRol(
        id_usuario=usuario_ejemplo.id_usuario,
        id_rol=rol.id_rol
    )
    db.add(usuario_rol)
    db.commit()
    db.refresh(usuario_ejemplo)
    return usuario_ejemplo


def test_endpoint_admin_sin_rol(client, token_usuario):
    """Acceder a endpoint de admin sin rol debe fallar."""
    response = client.delete(
        "/api/v1/ligas/1",
        headers={"Authorization": f"Bearer {token_usuario}"}
    )

    assert response.status_code == 403
```

## Ejecutar Tests

```bash
# Ejecutar todos
pytest

# Con detalle
pytest -v

# Archivo específico
pytest tests/test_auth.py

# Test específico
pytest tests/test_auth.py::test_login_correcto

# Con patrón
pytest -k "login"

# Mostrar prints
pytest -s

# Cobertura
pytest --cov=app

# Cobertura HTML
pytest --cov=app --cov-report=html
```

### `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --cov=app --cov-report=term-missing
```

## Cobertura de Código

```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir reporte
open htmlcov/index.html
```

### Configurar cobertura mínima

```ini
# setup.cfg
[coverage:run]
source = app
omit =
    */tests/*
    */__init__.py

[coverage:report]
fail_under = 80
```

## Buenas Prácticas

### Tests independientes

```python
# ✅ Correcto
def test_crear_usuario(db):
    usuario = crear_usuario(db, datos)
    assert usuario.id_usuario is not None

# ❌ Evitar
def test_crear_usuario(db):
    global usuario_creado
    usuario_creado = crear_usuario(db, datos)

def test_eliminar_usuario(db):
    eliminar_usuario(db, usuario_creado.id_usuario)  # Depende del anterior
```

### Un concepto por test

```python
# ✅ Correcto
def test_crear_usuario_email_valido():
    pass

def test_crear_usuario_nombre_requerido():
    pass

# ❌ Evitar
def test_crear_usuario():
    # Prueba muchas cosas
    pass
```

### Nombres descriptivos

```python
# ✅ Correcto
def test_crear_usuario_con_email_duplicado_devuelve_error():
    pass

# ❌ Evitar
def test_error():
    pass
```