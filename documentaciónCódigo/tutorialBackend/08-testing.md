# Testing: Probar Tu Código (Para Principiantes)

## ¿Por Qué Hacer Tests?

Imagina que construyes un coche. Antes de venderlo, ¿no lo probarías?

- ¿Arranca el motor?
- ¿Frenan los frenos?
- ¿Gira el volante?
- ¿Las luces funcionan?

**Los tests son iguales:** verifican que tu código funcione correctamente.

### Sin Tests (❌)

```
1. Escribes código
2. Lo pruebas manualmente en Postman
3. Lo subes a producción
4. ¡Los usuarios encuentran errores!
5. Arreglas el error
6. Vuelves a probar manualmente
7. Repites para siempre...
```

**Problemas:**
- Lento y tedioso
- Fácil olvidar probar algo
- Los errores vuelven (regresiones)
- Difícil refactorizar

### Con Tests (✅)

```
1. Escribes código
2. Escribes tests automáticos
3. Ejecutas: pytest
4. ¡Todo pasa en 2 segundos!
5. Refactorizas con confianza
6. Los tests te avisan si rompes algo
```

**Ventajas:**
- Rápido (segundos, no minutos)
- Automático
- Documenta el comportamiento esperado
- Previene regresiones

---

## Configurar Pytest

### Instalar

```bash
pip install pytest pytest-cov httpx
```

| Librería | Para qué sirve |
|----------|---------------|
| `pytest` | Ejecutar tests |
| `pytest-cov` | Medir cobertura de código |
| `httpx` | Hacer peticiones HTTP en tests |

### Estructura de Carpetas

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Configuración compartida
│   ├── test_auth.py         # Tests de autenticación
│   ├── test_usuarios.py     # Tests de usuarios
│   └── test_ligas.py        # Tests de ligas
├── pytest.ini
└── requirements.txt
```

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --cov=app --cov-report=term-missing
```

---

## Fixtures: Datos de Prueba

### ¿Qué es un Fixture?

Un **fixture** es como un **preparativo** que se ejecuta antes de cada test:

```
┌─────────────────────────────────────────────┐
│              TEST                             │
├─────────────────────────────────────────────┤
│  1. Fixture: Crear base de datos de prueba   │
│  2. Fixture: Crear usuario de prueba         │
│  3. Test: Probar que funciona                 │
│  4. Fixture: Limpiar todo                     │
└─────────────────────────────────────────────┘
```

### conftest.py

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.main import app
from app.api.dependencies import get_db

# Base de datos en memoria (muy rápida, no persiste)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Crea una base de datos en memoria para cada test.
    Se limpia automáticamente después del test.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    # Crear sesión
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

    # Eliminar todas las tablas
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Crea un cliente de prueba para hacer peticiones HTTP.
    """
    from fastapi.testclient import TestClient

    # Sobrescribir la dependencia get_db
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Crear cliente
    with TestClient(app) as c:
        yield c

    # Limpiar
    app.dependency_overrides = {}


@pytest.fixture
def usuario_ejemplo(db):
    """
    Crea un usuario de prueba.
    """
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
    """
    Obtiene un token JWT para el usuario de prueba.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_ejemplo.email,
            "password": "password123"
        }
    )
    return response.json()["access_token"]
```

### ¿Qué hace cada fixture?

| Fixture | ¿Qué hace? | Cuándo usar |
|---------|------------|-------------|
| `db` | Crea BD en memoria | Tests que necesitan BD |
| `client` | Crea cliente HTTP | Tests de API |
| `usuario_ejemplo` | Crea usuario | Tests que necesitan usuario |
| `token_usuario` | Crea token JWT | Tests que necesitan autenticación |

---

## Tests de Servicios

### ¿Qué probamos en un servicio?

```python
# tests/test_usuario_service.py
import pytest
from app.api.services.usuario_service import (
    crear_usuario,
    obtener_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario
)
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


def test_crear_usuario(db):
    """Test: Crear un usuario correctamente."""
    # Preparar
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )

    # Ejecutar
    usuario = crear_usuario(db, datos)

    # Verificar
    assert usuario.id_usuario is not None
    assert usuario.nombre == "Juan García"
    assert usuario.email == "juan@email.com"
    assert usuario.contraseña_hash != "mi_contraseña"  # ¡Hasheada!


def test_crear_usuario_email_duplicado(db):
    """Test: No permitir email duplicado."""
    # Crear primer usuario
    datos1 = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    crear_usuario(db, datos1)

    # Intentar crear segundo usuario con mismo email
    datos2 = UsuarioCreate(
        nombre="Otro Juan",
        email="juan@email.com",  # Mismo email
        password="otra_contraseña"
    )

    # Debe lanzar error
    with pytest.raises(ValueError, match="email ya está registrado"):
        crear_usuario(db, datos2)


def test_obtener_usuario_por_id(db):
    """Test: Obtener usuario por ID."""
    # Crear usuario
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    usuario_creado = crear_usuario(db, datos)

    # Buscar por ID
    usuario_encontrado = obtener_usuario_por_id(db, usuario_creado.id_usuario)

    # Verificar
    assert usuario_encontrado is not None
    assert usuario_encontrado.email == "juan@email.com"


def test_obtener_usuario_no_existente(db):
    """Test: Usuario no encontrado."""
    usuario = obtener_usuario_por_id(db, 999)  # ID que no existe
    assert usuario is None


def test_actualizar_usuario(db):
    """Test: Actualizar usuario."""
    # Crear usuario
    datos_crear = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    usuario = crear_usuario(db, datos_crear)

    # Actualizar
    datos_actualizar = UsuarioUpdate(nombre="Juan Carlos")
    usuario_actualizado = actualizar_usuario(db, usuario.id_usuario, datos_actualizar)

    # Verificar
    assert usuario_actualizado.nombre == "Juan Carlos"
    assert usuario_actualizado.email == "juan@email.com"  # No cambió


def test_eliminar_usuario(db):
    """Test: Eliminar usuario."""
    # Crear usuario
    datos = UsuarioCreate(
        nombre="Juan García",
        email="juan@email.com",
        password="mi_contraseña"
    )
    usuario = crear_usuario(db, datos)

    # Eliminar
    eliminar_usuario(db, usuario.id_usuario)

    # Verificar que ya no existe
    usuario_eliminado = obtener_usuario_por_id(db, usuario.id_usuario)
    assert usuario_eliminado is None
```

### ¿Qué es `assert`?

`assert` verifica que algo sea verdadero:

```python
# Si es verdadero, pasa
assert 1 + 1 == 2  # ✅ Pasa

# Si es falso, falla
assert 1 + 1 == 3  # ❌ Falla: AssertionError
```

### ¿Qué es `pytest.raises`?

Verifica que se lance una excepción:

```python
def test_email_duplicado():
    with pytest.raises(ValueError, match="email ya está registrado"):
        crear_usuario(db, datos_duplicados)
    # Si NO se lanza la excepción, el test falla
```

---

## Tests de API

### ¿Qué probamos en un endpoint?

```python
# tests/test_auth.py


def test_login_correcto(client, usuario_ejemplo):
    """Test: Login con credenciales correctas."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_ejemplo.email,
            "password": "password123"
        }
    )

    # Verificar status code
    assert response.status_code == 200

    # Verificar respuesta
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_password_incorrecta(client, usuario_ejemplo):
    """Test: Login con contraseña incorrecta."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_ejemplo.email,
            "password": "contraseña_incorrecta"
        }
    )

    # Verificar status code
    assert response.status_code == 401


def test_obtener_perfil_sin_token(client):
    """Test: Acceder a perfil sin token."""
    response = client.get("/api/v1/auth/me")

    # Debe devolver 401 Unauthorized
    assert response.status_code == 401


def test_obtener_perfil_con_token(client, token_usuario):
    """Test: Acceder a perfil con token válido."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_usuario}"}
    )

    # Verificar status code
    assert response.status_code == 200

    # Verificar respuesta
    data = response.json()
    assert "email" in data
    assert data["email"] == "test@email.com"
```

```python
# tests/test_usuarios.py


def test_crear_usuario(client):
    """Test: Crear un usuario."""
    response = client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Nuevo Usuario",
            "email": "nuevo@email.com",
            "password": "password123"
        }
    )

    # Verificar status code
    assert response.status_code == 201

    # Verificar respuesta
    data = response.json()
    assert data["nombre"] == "Nuevo Usuario"
    assert "password" not in data  # No debe incluir contraseña


def test_crear_usuario_email_duplicado(client):
    """Test: No permitir email duplicado."""
    # Crear primer usuario
    client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Usuario 1",
            "email": "test@email.com",
            "password": "password123"
        }
    )

    # Intentar crear segundo con mismo email
    response = client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Usuario 2",
            "email": "test@email.com",  # Mismo email
            "password": "password456"
        }
    )

    # Debe fallar
    assert response.status_code == 400


def test_listar_usuarios(client):
    """Test: Listar usuarios."""
    # Crear algunos usuarios
    for i in range(3):
        client.post(
            "/api/v1/usuarios/",
            json={
                "nombre": f"Usuario {i}",
                "email": f"usuario{i}@email.com",
                "password": "password123"
            }
        )

    # Listar
    response = client.get("/api/v1/usuarios/")

    # Verificar
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_obtener_usuario_por_id(client):
    """Test: Obtener usuario por ID."""
    # Crear usuario
    crear = client.post(
        "/api/v1/usuarios/",
        json={
            "nombre": "Usuario Test",
            "email": "test@email.com",
            "password": "password123"
        }
    )
    usuario_id = crear.json()["id_usuario"]

    # Obtener por ID
    response = client.get(f"/api/v1/usuarios/{usuario_id}")

    # Verificar
    assert response.status_code == 200
    assert response.json()["id_usuario"] == usuario_id


def test_obtener_usuario_no_existente(client):
    """Test: Usuario no encontrado."""
    response = client.get("/api/v1/usuarios/999")
    assert response.status_code == 404
```

---

## Tests con Roles

### Crear Usuario con Rol

```python
# tests/conftest.py
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol


@pytest.fixture
def usuario_admin(db, usuario_ejemplo):
    """Crea un usuario con rol admin."""
    # Crear rol
    rol = Rol(nombre="admin", descripcion="Administrador")
    db.add(rol)
    db.commit()
    db.refresh(rol)

    # Asignar rol al usuario
    usuario_rol = UsuarioRol(
        id_usuario=usuario_ejemplo.id_usuario,
        id_rol=rol.id_rol
    )
    db.add(usuario_rol)
    db.commit()
    db.refresh(usuario_ejemplo)

    return usuario_ejemplo


@pytest.fixture
def token_admin(client, usuario_admin):
    """Obtiene token para usuario admin."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": usuario_admin.email,
            "password": "password123"
        }
    )
    return response.json()["access_token"]
```

### Test de Autorización

```python
# tests/test_roles.py


def test_endpoint_admin_sin_rol(client, token_usuario):
    """Test: Acceder a endpoint de admin sin rol admin."""
    response = client.delete(
        "/api/v1/ligas/1",
        headers={"Authorization": f"Bearer {token_usuario}"}
    )

    # Debe devolver 403 Forbidden
    assert response.status_code == 403


def test_endpoint_admin_con_rol(client, token_admin):
    """Test: Acceder a endpoint de admin con rol admin."""
    # Primero crear una liga
    client.post(
        "/api/v1/ligas/",
        json={"nombre": "Liga Test"},
        headers={"Authorization": f"Bearer {token_admin}"}
    )

    # Intentar eliminar
    response = client.delete(
        "/api/v1/ligas/1",
        headers={"Authorization": f"Bearer {token_admin}"}
    )

    # Debe devolver 204 No Content
    assert response.status_code == 204
```

---

## Ejecutar Tests

### Comandos Básicos

```bash
# Ejecutar todos los tests
pytest

# Con más detalle
pytest -v

# Un archivo específico
pytest tests/test_auth.py

# Un test específico
pytest tests/test_auth.py::test_login_correcto

# Con patrón
pytest -k "login"

# Mostrar prints
pytest -s
```

### Medir Cobertura

```bash
# Ejecutar con cobertura
pytest --cov=app

# Ver líneas no cubiertas
pytest --cov=app --cov-report=term-missing

# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir reporte
open htmlcov/index.html
```

**¿Qué es la cobertura?**

La **cobertura** mide qué porcentaje de tu código ejecutan los tests:

```
---------- coverage: platform ----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
app/api/routers/auth.py          45      2    96%
app/api/routers/usuarios.py     120     15    88%
app/api/services/usuario.py      85      0   100%
-------------------------------------------------
TOTAL                           250     17    93%
```

- **Stmts**: Total de líneas de código
- **Miss**: Líneas NO ejecutadas por tests
- **Cover**: Porcentaje de cobertura

**Meta:** Apunta a **80%+** de cobertura.

---

## Buenas Prácticas

### 1. Tests Independientes

```python
# ❌ MALO - Tests dependen unos de otros
usuario_creado = None  # Variable global

def test_crear_usuario():
    global usuario_creado
    usuario_creado = crear_usuario(db, datos)  # Guarda estado

def test_eliminar_usuario():
    eliminar_usuario(db, usuario_creado.id_usuario)  # Depende del anterior


# ✅ BUENO - Tests independientes
def test_crear_usuario(db):
    usuario = crear_usuario(db, datos)
    assert usuario.id_usuario is not None

def test_eliminar_usuario(db):
    # Crear usuario para este test específico
    usuario = crear_usuario(db, datos)
    eliminar_usuario(db, usuario.id_usuario)
    assert obtener_usuario(db, usuario.id_usuario) is None
```

### 2. Un Concepto por Test

```python
# ❌ MALO - Un test prueba muchas cosas
def test_usuario():
    # Test crear
    usuario = crear_usuario(db, datos)
    assert usuario is not None

    # Test actualizar
    usuario.nombre = "Nuevo"
    assert usuario.nombre == "Nuevo"

    # Test eliminar
    eliminar_usuario(db, usuario.id_usuario)
    assert obtener_usuario(db, usuario.id_usuario) is None


# ✅ BUENO - Un test por concepto
def test_crear_usuario(db):
    usuario = crear_usuario(db, datos)
    assert usuario is not None

def test_actualizar_usuario(db):
    usuario = crear_usuario(db, datos)
    actualizar_usuario(db, usuario.id_usuario, UsuarioUpdate(nombre="Nuevo"))
    assert usuario.nombre == "Nuevo"

def test_eliminar_usuario(db):
    usuario = crear_usuario(db, datos)
    eliminar_usuario(db, usuario.id_usuario)
    assert obtener_usuario(db, usuario.id_usuario) is None
```

### 3. Nombres Descriptivos

```python
# ❌ MALO - Nombre confuso
def test_error():
    ...

def test_usuario():
    ...

# ✅ BUENO - Nombre descriptivo
def test_crear_usuario_con_email_duplicado_devuelve_error():
    ...

def test_login_con_password_incorrecta_devuelve_401():
    ...
```

### 4. Estructura AAA

```python
def test_nombre():
    # Arrange (Preparar)
    datos = UsuarioCreate(nombre="Juan", email="juan@email.com", password="123")

    # Act (Ejecutar)
    usuario = crear_usuario(db, datos)

    # Assert (Verificar)
    assert usuario.id_usuario is not None
    assert usuario.email == "juan@email.com"
```

---

## Resumen

Aprendiste:

1. **Tests** = Verificar que tu código funciona
2. **Fixtures** = Datos de prueba que se preparan automáticamente
3. **pytest** = Herramienta para ejecutar tests
4. **Cobertura** = Porcentaje de código probado
5. **Buenas prácticas** = Tests independientes, un concepto por test, nombres descriptivos

**¿Listo para el último paso?**

Ve a **09-despliegue.md** para aprender cómo poner tu app en producción.