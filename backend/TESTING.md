# 🧪 Guía de Testing - GoalApp

Documentación completa para ejecutar y crear tests en el proyecto GoalApp.

## 📋 Tabla de Contenidos

1. [Instalación](#instalación)
2. [Estructura de Tests](#estructura-de-tests)
3. [Ejecutar Tests](#ejecutar-tests)
4. [Tipos de Tests](#tipos-de-tests)
5. [Fixtures Disponibles](#fixtures-disponibles)
6. [Crear Nuevos Tests](#crear-nuevos-tests)
7. [Buenas Prácticas](#buenas-prácticas)
8. [Solución de Problemas](#solución-de-problemas)

---

## 📦 Instalación

### 1. Instalar Dependencias

```powershell
cd backend
pip install -r requirements.txt
```

Las dependencias de testing incluyen:
- `pytest` - Framework de testing
- `pytest-asyncio` - Soporte para tests asíncronos
- `httpx` - Cliente HTTP para FastAPI TestClient
- `faker` - Generación de datos de prueba

### 2. Verificar Instalación

```powershell
pytest --version
```

---

## 📁 Estructura de Tests

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Configuración global y fixtures
│   ├── unit/                    # Tests unitarios
│   │   ├── __init__.py
│   │   ├── test_usuario_service.py
│   │   └── test_liga_service.py
│   └── integration/             # Tests de integración
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_usuarios.py
│       └── test_ligas.py
├── pytest.ini                   # Configuración de pytest
└── app/                         # Código de la aplicación
```

### Descripción de Archivos

| Archivo | Propósito |
|---------|-----------|
| `conftest.py` | Fixtures compartidos y configuración global |
| `pytest.ini` | Configuración de pytest (markers, logging, etc.) |
| `test_*.py` | Archivos de tests (deben empezar con `test_`) |
| `unit/` | Tests que prueban componentes individuales |
| `integration/` | Tests que prueban el flujo completo de endpoints |

---

## 🚀 Ejecutar Tests

### Todos los Tests

```powershell
cd backend
pytest
```

### Tests con Salida Detallada

```powershell
pytest -v
```

### Tests de una Categoría Específica

```powershell
# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/
```

### Test Específico

```powershell
# Por archivo
pytest tests/integration/test_auth.py

# Por función
pytest tests/integration/test_auth.py::test_login_success

# Por patrón de nombre
pytest -k "login"
```

### Con Coverage (Cobertura)

```powershell
# Instalar pytest-cov primero
pip install pytest-cov

# Ejecutar con coverage
pytest --cov=app --cov-report=html

# Ver reporte en navegador
start htmlcov/index.html  # Windows
```

### Opciones Útiles

```powershell
# Detener en el primer fallo
pytest -x

# Mostrar prints durante tests
pytest -s

# Ejecutar tests en paralelo (requiere pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Ver tests más lentos
pytest --durations=10
```

---

## 🧪 Tipos de Tests

### 1. Tests de Integración

Prueban el flujo completo de la API (endpoints).

**Ejemplo:** `tests/integration/test_auth.py`

```python
def test_login_success(client, sample_usuario_data):
    """Test de login exitoso"""
    # Crear usuario
    client.post("/api/v1/usuarios/", json=sample_usuario_data)
    
    # Login
    login_data = {
        "username": sample_usuario_data["email"],
        "password": sample_usuario_data["contraseña"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
```

**¿Qué prueban?**
- ✅ Endpoints completos (request → response)
- ✅ Autenticación y autorización
- ✅ Validación de datos
- ✅ Códigos de estado HTTP
- ✅ Estructura de respuestas JSON

### 2. Tests Unitarios

Prueban funciones individuales de services y utilidades.

**Ejemplo:** `tests/unit/test_usuario_service.py`

```python
def test_hash_password():
    """Test de hasheo de contraseña"""
    password = "password123"
    hashed = usuario_service.hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 20
    assert hashed.startswith("$2b$")
```

**¿Qué prueban?**
- ✅ Lógica de negocio aislada
- ✅ Funciones de utilidad
- ✅ Transformaciones de datos
- ✅ Validaciones

---

## 🎯 Fixtures Disponibles

Los fixtures son funciones que proporcionan datos o configuración reutilizable para los tests.

### Definidos en `conftest.py`

#### 1. `client`
Cliente de prueba de FastAPI.

```python
def test_example(client):
    response = client.get("/health")
    assert response.status_code == 200
```

#### 2. `db_session`
Sesión de base de datos de prueba (SQLite en memoria).

```python
def test_example(db_session):
    from app.models.usuario import Usuario
    
    usuario = Usuario(nombre="Test", email="test@test.com")
    db_session.add(usuario)
    db_session.commit()
```

#### 3. `sample_usuario_data`
Datos de ejemplo para crear un usuario.

```python
def test_example(sample_usuario_data):
    # sample_usuario_data = {
    #     "nombre": "Juan Pérez",
    #     "email": "juan@example.com",
    #     "contraseña": "password123"
    # }
    assert "email" in sample_usuario_data
```

#### 4. `sample_liga_data`
Datos de ejemplo para crear una liga.

```python
def test_example(sample_liga_data):
    # sample_liga_data = {
    #     "nombre": "Liga Madrid",
    #     "temporada": "2024/2025"
    # }
    assert "temporada" in sample_liga_data
```

#### 5. `sample_equipo_data`
Datos de ejemplo para crear un equipo.

```python
def test_example(sample_equipo_data):
    assert "nombre" in sample_equipo_data
```

#### 6. `auth_token`
Token JWT de autenticación (crea usuario y hace login automáticamente).

```python
def test_example(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/usuarios/", headers=headers)
    assert response.status_code == 200
```

#### 7. `auth_headers`
Headers de autenticación listos para usar.

```python
def test_example(client, auth_headers):
    response = client.get("/api/v1/usuarios/", headers=auth_headers)
    assert response.status_code == 200
```

---

## ✍️ Crear Nuevos Tests

### Test de Integración (Endpoint)

**Archivo:** `tests/integration/test_equipos.py`

```python
# tests/integration/test_equipos.py
"""Tests de integración para endpoints de equipos."""
import pytest


def test_create_equipo(client, auth_headers):
    """Test de creación de equipo"""
    # Primero crear una liga (dependencia)
    liga_data = {"nombre": "Liga Test", "temporada": "2024/2025"}
    liga_response = client.post("/api/v1/ligas/", json=liga_data, headers=auth_headers)
    liga_id = liga_response.json()["id_liga"]
    
    # Crear usuario entrenador y delegado
    entrenador_data = {"nombre": "Entrenador", "email": "coach@test.com", "contraseña": "pass123"}
    entrenador_response = client.post("/api/v1/usuarios/", json=entrenador_data)
    entrenador_id = entrenador_response.json()["id_usuario"]
    
    # Crear equipo
    equipo_data = {
        "nombre": "CD Test",
        "id_liga": liga_id,
        "id_entrenador": entrenador_id,
        "id_delegado": entrenador_id
    }
    response = client.post("/api/v1/equipos/", json=equipo_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "CD Test"


def test_list_equipos(client, auth_headers):
    """Test de listado de equipos"""
    response = client.get("/api/v1/equipos/", headers=auth_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Test Unitario (Service)

**Archivo:** `tests/unit/test_equipo_service.py`

```python
# tests/unit/test_equipo_service.py
"""Tests unitarios para equipo_service."""
import pytest
from app.api.services import equipo_service


def test_crear_equipo(db_session):
    """Test de creación de equipo"""
    from app.schemas.equipo import EquipoCreate
    from app.schemas.liga import LigaCreate
    from app.schemas.usuario import UsuarioCreate
    from app.api.services import liga_service, usuario_service
    
    # Crear dependencias
    liga = liga_service.crear_liga(db_session, LigaCreate(nombre="Liga", temporada="2024"))
    usuario = usuario_service.crear_usuario(
        db_session,
        UsuarioCreate(nombre="Coach", email="coach@test.com", contraseña="pass")
    )
    
    # Crear equipo
    equipo_data = EquipoCreate(
        nombre="CD Test",
        id_liga=liga.id_liga,
        id_entrenador=usuario.id_usuario,
        id_delegado=usuario.id_usuario
    )
    equipo = equipo_service.crear_equipo(db_session, equipo_data)
    
    assert equipo.id_equipo is not None
    assert equipo.nombre == "CD Test"
```

### Estructura de un Test

```python
def test_nombre_descriptivo(client, auth_headers):
    """
    Docstring explicando qué prueba el test.
    """
    # 1. ARRANGE - Preparar datos y estado inicial
    data = {"campo": "valor"}
    
    # 2. ACT - Ejecutar la acción que se está probando
    response = client.post("/api/v1/endpoint/", json=data, headers=auth_headers)
    
    # 3. ASSERT - Verificar el resultado
    assert response.status_code == 201
    assert response.json()["campo"] == "valor"
```

---

## ✅ Buenas Prácticas

### 1. Nombres Descriptivos

❌ Mal:
```python
def test_1(client):
    ...
```

✅ Bien:
```python
def test_create_usuario_with_valid_data(client, sample_usuario_data):
    ...
```

### 2. Un Concepto por Test

❌ Mal:
```python
def test_usuarios(client):
    # Prueba crear, listar, actualizar y eliminar
    ...
```

✅ Bien:
```python
def test_create_usuario(client):
    ...

def test_list_usuarios(client):
    ...

def test_update_usuario(client):
    ...
```

### 3. Usar Fixtures

❌ Mal:
```python
def test_login(client):
    # Crear usuario manualmente cada vez
    client.post("/api/v1/usuarios/", json={
        "nombre": "Test",
        "email": "test@test.com",
        "contraseña": "pass"
    })
    ...
```

✅ Bien:
```python
def test_login(client, sample_usuario_data):
    # Usar fixture con datos de ejemplo
    client.post("/api/v1/usuarios/", json=sample_usuario_data)
    ...
```

### 4. Independencia de Tests

Cada test debe ser independiente y no depender del resultado de otros.

❌ Mal:
```python
usuario_id = None

def test_create_usuario(client):
    global usuario_id
    response = client.post(...)
    usuario_id = response.json()["id"]

def test_get_usuario(client):
    # Depende del test anterior
    response = client.get(f"/usuarios/{usuario_id}")
```

✅ Bien:
```python
def test_create_usuario(client, sample_usuario_data):
    response = client.post("/api/v1/usuarios/", json=sample_usuario_data)
    assert response.status_code == 201

def test_get_usuario(client, sample_usuario_data):
    # Crear usuario dentro del test
    create_response = client.post("/api/v1/usuarios/", json=sample_usuario_data)
    usuario_id = create_response.json()["id_usuario"]
    
    response = client.get(f"/api/v1/usuarios/{usuario_id}")
    assert response.status_code == 200
```

### 5. Assertions Claras

❌ Mal:
```python
assert response
```

✅ Bien:
```python
assert response.status_code == 200
assert "id_usuario" in response.json()
assert response.json()["email"] == "test@example.com"
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'app'"

**Problema:** Python no encuentra el módulo `app`

**Solución:**
```powershell
# Asegúrate de estar en el directorio backend/
cd backend
pytest

# O establece PYTHONPATH
$env:PYTHONPATH = "."
pytest
```

### Error: "fixture 'xxx' not found"

**Problema:** Fixture no está definido o no se encuentra

**Solución:**
- Verifica que el fixture esté en `conftest.py`
- Verifica que el nombre del fixture sea correcto
- Ejecuta desde el directorio correcto: `backend/`

### Tests Fallando por Base de Datos

**Problema:** Conflictos con base de datos real

**Solución:**
Los tests usan SQLite en memoria por defecto (definido en `conftest.py`). No afectan a tu base de datos MySQL real.

### Error: "Address already in use"

**Problema:** El puerto está ocupado

**Solución:**
Los tests usan `TestClient` que no requiere puerto. Si ves este error, cierra el servidor de desarrollo antes de ejecutar tests.

### Tests Lentos

**Problema:** Los tests tardan mucho

**Solución:**
```powershell
# Ejecutar en paralelo
pip install pytest-xdist
pytest -n auto

# Ver cuáles son más lentos
pytest --durations=10
```

---

## 📊 Ejemplo de Ejecución Completa

```powershell
# 1. Navegar al directorio backend
cd backend

# 2. Ejecutar todos los tests
pytest

# Salida esperada:
# ============================== test session starts ==============================
# platform win32 -- Python 3.10.0, pytest-7.4.0, pluggy-1.3.0
# rootdir: C:\...\GoalApp\backend
# configfile: pytest.ini
# collected 25 items
#
# tests\integration\test_auth.py ......                                    [ 24%]
# tests\integration\test_ligas.py .....                                    [ 44%]
# tests\integration\test_usuarios.py ........                              [ 76%]
# tests\unit\test_liga_service.py .....                                    [ 96%]
# tests\unit\test_usuario_service.py .                                     [100%]
#
# ============================== 25 passed in 5.23s ===============================
```

---

## 🎓 Recursos Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

---

## 📝 Resumen de Comandos

```powershell
# Instalación
pip install -r requirements.txt

# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/integration/test_auth.py
pytest -k "login"

# Con opciones útiles
pytest -v              # Verbose
pytest -x              # Stop at first failure
pytest -s              # Show prints
pytest --durations=10  # Show slowest tests

# Con coverage
pytest --cov=app --cov-report=html
```

---

¡Los tests están listos para usar! 🎉
