# Despliegue en Producción

## Checklist de Seguridad

- Cambiar `SECRET_KEY` a un valor seguro
- Configurar `ENVIRONMENT=production`
- Desactivar `DATABASE_ECHO=False`
- Configurar CORS con dominios específicos
- Usar HTTPS
- Configurar rate limiting (opcional)

## Configuración de Producción

### `.env` de producción

```env
# Base de datos
DATABASE_URL=mysql+pymysql://goalapp:contraseña_segura@db.servidor.com:3306/futbol_app
DATABASE_ECHO=False

# Seguridad
SECRET_KEY=clave_muy_larga_y_segura_generada_con_secrets
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Aplicación
APP_NAME=Liga Amateur App
API_VERSION=v1
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0

# CORS
CORS_ORIGINS=https://midominio.com,https://www.midominio.com

# Logs
LOG_LEVEL=WARNING

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tuemail@gmail.com
SMTP_PASSWORD=app_password
EMAIL_FROM=tuemail@gmail.com
FRONTEND_URL=https://midominio.com
RESET_TOKEN_EXPIRE_MINUTES=30
```

## Opción 1: Gunicorn + Systemd

### Instalar Gunicorn

```bash
pip install gunicorn
```

### Ejecutar

```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5
```

### Systemd Service

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

```bash
sudo systemctl enable goalapp
sudo systemctl start goalapp
sudo systemctl status goalapp
```

## Opción 2: Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
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

volumes:
  mysql_data:
```

### Comandos Docker

```bash
docker-compose build
docker-compose up -d
docker-compose logs -f backend
docker-compose down
```

## Nginx como Proxy Inverso

### Configuración

```nginx
# /etc/nginx/sites-available/goalapp
server {
    listen 80;
    server_name api.midominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.midominio.com;

    ssl_certificate /etc/letsencrypt/live/api.midominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.midominio.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Habilitar sitio

```bash
sudo ln -s /etc/nginx/sites-available/goalapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL con Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.midominio.com
sudo certbot renew --dry-run
```

## Logs

### Configurar logging

```python
# app/main.py
import logging
from app.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Middleware para logging

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
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

## Copias de Seguridad

### Script de backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/mysql"
MYSQL_USER="goalapp"
MYSQL_PASSWORD="password"
DATABASE="futbol_app"

mkdir -p $BACKUP_DIR

mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $DATABASE > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

### Cron job

```bash
crontab -e

# Backup diario a las 2 AM
0 2 * * * /var/www/goalapp/scripts/backup.sh
```

## Migraciones con Alembic

### Configuración

```bash
pip install alembic
alembic init alembic
```

### `alembic/env.py`

```python
from app.database.connection import Base
from app.config import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

### Comandos

```bash
# Crear migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar
alembic upgrade head

# Revertir
alembic downgrade -1

# Historial
alembic history
```

## Health Check

```python
# app/main.py
from app.database.connection import engine

@app.get("/health")
async def health_check():
    try:
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

## Comandos Útiles

```bash
# Ver logs del servicio
sudo journalctl -u goalapp -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar servicios
sudo systemctl restart goalapp
sudo systemctl restart nginx

# Verificar puertos
sudo netstat -tlnp | grep 8000

# Verificar procesos
ps aux | grep gunicorn

# Test de carga
ab -n 1000 -c 10 http://localhost:8000/api/v1/

# Uso de memoria
free -h

# Uso de disco
df -h
```

## Checklist Final

### Antes del despliegue

- [ ] Variables de entorno configuradas
- [ ] Base de datos creada y migrada
- [ ] SSL configurado
- [ ] CORS configurado para dominios específicos
- [ ] Logs configurados
- [ ] Backups automáticos

### Después del despliegue

- [ ] Health check responde
- [ ] Login funciona
- [ ] Endpoints principales funcionan
- [ ] Logs sin errores
- [ ] SSL funciona