# Despliegue en Producción (Para Principiantes)

## ¿Qué es el Despliegue?

Imagina que construyes una casa:

```
DESARROLLO (Tu computadora)    →    PRODUCCIÓN (Internet)
┌─────────────────────────┐        ┌─────────────────────────┐
│  Código                 │        │  Servidor en la nube     │
│  Base de datos local    │   →    │  Base de datos real      │
│  Debug activado         │        │  Seguridad máxima        │
│  Solo tú la ves         │        │  Todo el mundo la ve     │
└─────────────────────────┘        └─────────────────────────┘
```

**El despliegue** es llevar tu aplicación del desarrollo a producción para que todos puedan usarla.

---

## Checklist de Seguridad

Antes de desplegar, revisa esto:

### ✅ Variables de Entorno

```env
# ❌ NUNCA uses valores de desarrollo
SECRET_KEY=secret
DEBUG=True
DATABASE_URL=sqlite:///test.db

# ✅ Usa valores de producción
SECRET_KEY=jX9kL2mN4pQ8rT6vW3yZ5aB7cD9eF1gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0
DEBUG=False
DATABASE_URL=mysql+pymysql://user:password@server:3306/production_db
```

### ✅ Claves Secretas

```bash
# Generar SECRET_KEY seguro
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Resultado: jX9kL2mN4pQ8rT6vW3yZ5aB7cD9eF1gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0
```

**Nunca uses:** "secret", "password", "mi_clave", etc.

### ✅ CORS

```python
# ❌ NUNCA uses ["*"] en producción
allow_origins = ["*"]  # Permite CUALQUIER dominio

# ✅ Especifica dominios permitidos
allow_origins = ["https://midominio.com", "https://www.midominio.com"]
```

### ✅ Debug Desactivado

```python
# ❌ En desarrollo
DATABASE_ECHO=True   # Muestra SQL en consola

# ✅ En producción
DATABASE_ECHO=False  # No muestra SQL
```

### ✅ HTTPS

Nunca uses HTTP en producción. Siempre HTTPS.

---

## Opción 1: Gunicorn + Systemd

### ¿Qué es Gunicorn?

**Uvicorn** es para desarrollo. **Gunicorn** es para producción.

```
Uvicorn: Un solo worker (proceso)
┌─────────────────────┐
│     Uvicorn         │
│   (1 proceso)       │
└─────────────────────┘

Gunicorn: Múltiples workers
┌─────────────────────┐
│     Gunicorn        │
│  ┌───┐ ┌───┐ ┌───┐ │
│  │ W │ │ W │ │ W │ │  ← 3 workers
│  └───┘ └───┘ └───┘ │
└─────────────────────┘
```

### Instalar Gunicorn

```bash
pip install gunicorn
```

### Ejecutar

```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

**¿Qué significa cada opción?**

| Opción | Significado |
|--------|-------------|
| `--workers 4` | 4 procesos manejando peticiones |
| `--worker-class uvicorn.workers.UvicornWorker` | Usa Uvicorn para apps async |
| `--bind 0.0.0.0:8000` | Escucha en puerto 8000 |

**¿Cuántos workers?**

```
workers = (2 × CPUs) + 1
```

Si tienes 2 CPUs: workers = (2 × 2) + 1 = 5

### Systemd Service

Crea un servicio para que tu app se inicie automáticamente:

```ini
# /etc/systemd/system/goalapp.service
[Unit]
Description=GoalApp Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/goalapp/backend
Environment="PATH=/var/www/goalapp/backend/.venv/bin"
ExecStart=/var/www/goalapp/backend/.venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Comandos útiles:**

```bash
# Iniciar el servicio
sudo systemctl start goalapp

# Detener el servicio
sudo systemctl stop goalapp

# Reiniciar el servicio
sudo systemctl restart goalapp

# Ver el estado
sudo systemctl status goalapp

# Ver logs
sudo journalctl -u goalapp -f

# Iniciar automáticamente al encender
sudo systemctl enable goalapp
```

---

## Opción 2: Docker

### ¿Qué es Docker?

**Docker** es como una **caja sellada** que contiene todo lo que tu app necesita:

```
┌─────────────────────────────────────────────┐
│              CONTENEDOR DOCKER               │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │  App (FastAPI)                      │   │
│  ├─────────────────────────────────────┤   │
│  │  Python + Dependencias             │   │
│  ├─────────────────────────────────────┤   │
│  │  Sistema Operativo (Linux)         │   │
│  └─────────────────────────────────────┘   │
│                                            │
│  ¡Todo incluido, listo para funcionar!    │
└─────────────────────────────────────────────┘
```

**Ventajas:**

- Funciona igual en cualquier computadora
- Fácil de desplegar
- Aislado del resto del sistema
- Fácil de escalar

### Dockerfile

```dockerfile
# Usar Python 3.11 como base
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para caché)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar
CMD ["gunicorn", "app.main:app", "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Tu aplicación
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://goalapp:password@db:3306/futbol_app
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    restart: always

  # Base de datos
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=futbol_app
      - MYSQL_USER=goalapp
      - MYSQL_PASSWORD=password
    volumes:
      - mysql_data:/var/lib/mysql
    restart: always

# Persistencia de datos
volumes:
  mysql_data:
```

### Comandos Docker

```bash
# Construir la imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down

# Ver contenedores corriendo
docker ps

# Entrar a un contenedor
docker exec -it goalapp_backend_1 bash
```

---

## Nginx como Proxy Inverso

### ¿Qué es Nginx?

**Nginx** es como un **recepcionista** que recibe las peticiones y las distribuye:

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          NGINX                                   │
│                     (El recepcionista)                          │
│                                                                 │
│  "Hola, ¿qué necesitas?"                                        │
│  "Ah, es una petición HTTPS, la encripto"                      │
│  "Ahora te la paso a Gunicorn"                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GUNICORN                                 │
│                     (Tu aplicación)                              │
└─────────────────────────────────────────────────────────────────┘
```

**¿Por qué usar Nginx?**

| Característica | Gunicorn solo | Gunicorn + Nginx |
|-----------------|---------------|-------------------|
| SSL/HTTPS | ❌ Complejo | ✅ Fácil |
| Archivos estáticos | ❌ Lento | ✅ Rápido |
| Rate limiting | ❌ No | ✅ Sí |
| Balanceo de carga | ❌ No | ✅ Sí |
| Compresión gzip | ❌ No | ✅ Sí |

### Configuración de Nginx

```nginx
# /etc/nginx/sites-available/goalapp

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name api.midominio.com;
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name api.midominio.com;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.midominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.midominio.com/privkey.pem;

    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Enviar peticiones a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Habilitar el Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/goalapp /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## SSL con Let's Encrypt

### ¿Qué es SSL?

**SSL** (ahora TLS) encripta la comunicación entre el navegador y tu servidor:

```
Sin SSL:
Cliente ────────────────────────────────────────── Servidor
         "hola" (texto plano, cualquiera puede leer)

Con SSL:
Cliente ────────────────────────────────────────── Servidor
         "kjsd87&*#$ksjd" (encriptado, nadie puede leer)
```

### Instalar Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d api.midominio.com

# Renovar automáticamente (probando)
sudo certbot renew --dry-run
```

**Certbot automáticamente:**
1. Verifica que eres dueño del dominio
2. Genera certificados SSL
3. Configura Nginx
4. Configura renovación automática

---

## Logs y Monitoreo

### Ver Logs

```bash
# Logs de tu aplicación (con systemd)
sudo journalctl -u goalapp -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Logs de MySQL
sudo tail -f /var/log/mysql/error.log
```

### Middleware de Logging

```python
# app/main.py
import time
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    return response
```

### Health Check

```python
# app/main.py
from app.database.connection import engine

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar que la app está viva.
    """
    try:
        # Verificar conexión a base de datos
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }
```

---

## Copias de Seguridad

### Script de Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/mysql"
MYSQL_USER="goalapp"
MYSQL_PASSWORD="tu_contraseña_segura"
DATABASE="futbol_app"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Hacer backup
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $DATABASE > $BACKUP_DIR/backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/backup_$DATE.sql

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completado: backup_$DATE.sql.gz"
```

### Programar con Cron

```bash
# Editar crontab
crontab -e

# Añadir línea para backup diario a las 2 AM
0 2 * * * /var/www/goalapp/scripts/backup.sh
```

---

## Migraciones en Producción

### Con Alembic

```bash
# Ver migraciones pendientes
alembic current
alembic history

# Crear migración
alembic revision --autogenerate -m "añadir campo telefono"

# Aplicar migración
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

**⚠️ IMPORTANTE:** Siempre revisa el archivo generado antes de aplicar:

```python
# alembic/versions/xxx_añadir_telefono.py

def upgrade():
    # ¿Está correcto?
    op.add_column('usuarios', sa.Column('telefono', sa.String(20)))

def downgrade():
    # ¿Está correcto?
    op.drop_column('usuarios', 'telefono')
```

---

## Comandos Útiles

### Verificar Estado

```bash
# Verificar que la app está corriendo
curl http://localhost:8000/health

# Verificar puertos
sudo netstat -tlnp | grep 8000

# Verificar procesos
ps aux | grep gunicorn

# Uso de memoria
free -h

# Uso de disco
df -h
```

### Reiniciar Servicios

```bash
# Reiniciar aplicación
sudo systemctl restart goalapp

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar MySQL
sudo systemctl restart mysql
```

### Debug

```bash
# Ver logs en tiempo real
sudo journalctl -u goalapp -f

# Ver errores de Nginx
sudo tail -f /var/log/nginx/error.log

# Probar endpoint
curl -X GET http://localhost:8000/api/v1/health

# Test de carga
ab -n 1000 -c 10 http://localhost:8000/api/v1/
```

---

## Checklist Final

### Antes de Desplegar

- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generado con `secrets.token_urlsafe(64)`
- [ ] Base de datos creada
- [ ] Migraciones aplicadas (`alembic upgrade head`)
- [ ] SSL configurado
- [ ] CORS configurado (dominios específicos, no `["*"]`)
- [ ] Debug desactivado
- [ ] Logs configurados

### Después de Desplegar

- [ ] Health check funciona: `/health`
- [ ] Login funciona
- [ ] Endpoints principales funcionan
- [ ] Logs sin errores
- [ ] SSL funciona (HTTPS)
- [ ] Backups programados

---

## Resumen

Aprendiste:

1. **Despliegue** = Llevar tu app a producción
2. **Seguridad** = SECRET_KEY, CORS, HTTPS, Debug desactivado
3. **Gunicorn** = Servidor de producción con múltiples workers
4. **Systemd** = Servicio que inicia tu app automáticamente
5. **Docker** = Contenedores para despliegue fácil
6. **Nginx** = Proxy inverso para SSL y archivos estáticos
7. **Let's Encrypt** = Certificados SSL gratuitos
8. **Backups** = Copias de seguridad programadas

---

## ¿Ahora Qué?

¡Felicidades! Has completado todo el tutorial. Ahora sabes:

1. ✅ Instalar y configurar el proyecto
2. ✅ Entender la arquitectura
3. ✅ Trabajar con la base de datos
4. ✅ Validar datos con schemas
5. ✅ Escribir lógica de negocio
6. ✅ Crear endpoints HTTP
7. ✅ Implementar autenticación
8. ✅ Hacer tests
9. ✅ Desplegar en producción

**¡A crear algo increíble! 🚀**