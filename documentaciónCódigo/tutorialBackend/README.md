# Documentación del Backend GoalApp (Versión para Principiantes)

## ¿Qué es GoalApp?

**GoalApp es como una app para gestionar ligas de fútbol amateur.** Imagina que organizas una liga de fútbol con tus amigos y necesitas:

- Anotar qué equipos juegan
- Registrar los resultados de los partidos
- Saber quién ganó más partidos
- Ver la tabla de posiciones

**GoalApp hace todo eso por ti.**

El **backend** es la parte que nadie ve, pero que hace todo el trabajo. Es como la cocina de un restaurante: los clientes (el frontend) piden comida, y la cocina (el backend) prepara todo y lo envía.

---

## ¿Qué voy a aprender?

Esta documentación te enseñará a crear el "cerebro" de una aplicación web usando:

| Archivo | ¿Qué aprenderás? |
|---------|------------------|
| **01-instalacion-configuracion.md** | Cómo preparar tu computadora para trabajar |
| **02-arquitectura.md** | Cómo está organizado el código (como un edificio con pisos) |
| **03-base-datos.md** | Cómo guardar la información de forma ordenada |
| **04-schemas.md** | Cómo verificar que los datos estén correctos |
| **05-servicios.md** | Cómo escribir las reglas de tu aplicación |
| **06-routers.md** | Cómo crear las "puertas" para que otros usen tu app |
| **07-autenticacion.md** | Cómo saber quién es cada usuario |
| **08-testing.md** | Cómo probar que todo funcione bien |
| **09-despliegue.md** | Cómo poner tu app en internet para que todos la usen |

---

## Las Herramientas que Usaremos

Imagina que vas a construir una casa. Necesitas diferentes herramientas para diferentes cosas. En programación es igual:

### FastAPI - El Constructor Principal

**FastAPI** es como un constructor muy rápido y organizado.

```
┌─────────────────────────────────────────────┐
│              FASTAPI                         │
│   (Organiza todo el trabajo)                │
├─────────────────────────────────────────────┤
│              SQLAlchemy                     │
│   (Guarda y busca datos)                    │
├─────────────────────────────────────────────┤
│              MySQL / SQLite                 │
│   (El lugar donde se guardan los datos)     │
└─────────────────────────────────────────────┘
```

**¿Para qué sirve cada uno?**

| Herramienta | ¿Qué hace? | Analogía |
|-------------|------------|----------|
| **FastAPI** | Organiza todo, recibe pedidos, envía respuestas | El gerente del restaurante |
| **SQLAlchemy** | Traduce tu código a lenguaje de base de datos | El traductor |
| **MySQL** | Guarda los datos permanentemente | La nevera gigante |

### Las Librerías que Necesitas

Una **librería** es código que alguien más ya escribió y tú puedes usar. Es como pedir prestada una herramienta:

```bash
# Estos son los "ingredientes" que necesitas
fastapi              # El constructor principal
uvicorn              # El servidor (como el mesero que lleva la comida)
sqlalchemy           # El traductor de base de datos
pymysql              # El cable que conecta con MySQL
pydantic             # El verificador de datos
python-jose          # Para crear "pases" de entrada (tokens)
passlib[bcrypt]      # Para esconder contraseñas de forma segura
```

---

## Cómo está Organizado Todo

Piensa en un restaurante:

```
┌─────────────────────────────────────────────────────────┐
│                    MESEROS                              │
│              (Routers - Reciben pedidos)               │
│         "Hola, ¿qué desea ordenar?"                    │
├─────────────────────────────────────────────────────────┤
│                    COCINA                               │
│              (Services - Preparan la comida)            │
│         "Aquí está tu hamburguesa"                     │
├─────────────────────────────────────────────────────────┤
│                    DESPENSA                             │
│              (Models - Donde están los ingredientes)    │
│         "El tomate está en la nevera"                  │
├─────────────────────────────────────────────────────────┤
│                    NEVERA                               │
│              (Base de datos - Guarda todo)              │
│         "Aquí guardamos la leche, los huevos..."       │
└─────────────────────────────────────────────────────────┘
```

**¿Cómo funciona un pedido?**

1. **El cliente** (frontend) hace un pedido: "Quiero ver todos los equipos"
2. **El mesero** (router) recibe el pedido y lo anota
3. **La cocina** (service) prepara la respuesta usando los ingredientes
4. **La despensa** (model) dice dónde están los ingredientes
5. **La nevera** (base de datos) tiene guardados los ingredientes
6. El pedido vuelve por el mismo camino hasta el cliente

---

## Cómo Fluye un Pedido (Ejemplo Real)

Imagina que alguien quiere ver la lista de equipos:

```
📱 Frontend → "Dame todos los equipos"

     ↓

🚪 Router (equipos.py)
   "Recibido. Voy a pedirle al servicio."

     ↓

👨‍🍳 Service (equipo_service.py)
   "Voy a buscar los equipos en la base de datos."

     ↓

📦 Model (equipo.py - ORM)
   "SQLAlchemy, traduce esto a SQL por favor."
   "SELECT * FROM equipos"

     ↓

🗄️ Base de datos (MySQL)
   "Aquí están los 10 equipos que guardé."

     ↓

📦 Model
   "Perfecto, aquí están convertidos a objetos Python."

     ↓

👨‍🍳 Service
   "Ya los tengo. Aquí están listos."

     ↓

🚪 Router
   "Perfecto. Voy a enviar la respuesta."
   [{"id": 1, "nombre": "Equipo A"}, ...]

     ↓

📱 Frontend
   "¡Gracias! Ahora muestro los equipos al usuario."
```

---

## Las Reglas del Juego (Convenciones)

Para que todos podamos entendernos, seguimos estas reglas:

### Todo en Español

```python
# ✅ BIEN - En español
def obtener_usuario():
    usuario = Usuario()
    return usuario

# ❌ MAL - En inglés
def get_user():
    user = User()
    return user
```

### Los Nombres Dicen lo que Hacen

```python
# ✅ BIEN - El nombre explica qué hace
def crear_usuario(db, datos):
    ...

def obtener_usuario_por_id(db, id_usuario):
    ...

def eliminar_usuario(db, id_usuario):
    ...

# ❌ MAL - Nombres confusos
def process(db, data):
    ...

def handle(id):
    ...
```

### Las Tablas en Plural

```python
# ✅ BIEN - Plural
class Usuario(Base):
    __tablename__ = "usuarios"  # Muchos usuarios viven aquí

class Equipo(Base):
    __tablename__ = "equipos"   # Muchos equipos viven aquí

# ❌ MAL - Singular
class Usuario(Base):
    __tablename__ = "usuario"   # ¿Solo cabe un usuario?
```

### Las Llaves Primarias con Prefijo `id_`

```python
# ✅ BIEN - Claro qué es
id_usuario = Column(Integer, primary_key=True)   # Es el ID del usuario
id_equipo = Column(Integer, primary_key=True)   # Es el ID del equipo

# ❌ MAL - Confuso
id = Column(Integer, primary_key=True)   # ¿De qué? ¿Del usuario? ¿Del equipo?
```

---

## Enlaces Útiles para Aprender Más

Estos son como libros de la biblioteca que te pueden ayudar:

- [Documentación de FastAPI](https://fastapi.tiangolo.com/) - El manual oficial de FastAPI
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/) - Todo sobre bases de datos
- [Documentación de Pydantic](https://docs.pydantic.dev/) - Cómo validar datos

---

## ¿Listo para Empezar?

Ve al archivo **01-instalacion-configuracion.md** para preparar tu computadora.

¡Vamos a construir algo genial! 🚀