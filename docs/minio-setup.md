# Guía de Configuración de MinIO para CupidoUP

Este documento describe cómo configurar MinIO como storage de objetos S3-compatible para el almacenamiento de imágenes de perfil en CupidoUP.

## ¿Qué es MinIO?

MinIO es un servidor de almacenamiento de objetos de alto rendimiento, compatible con la API de Amazon S3. Permite almacenar archivos (imágenes, documentos, etc.) de forma escalable y accesible via HTTP.

**Ventajas para CupidoUP:**
- Compatible con S3: fácil migración futura a AWS S3 u otros proveedores
- Self-hosted: control total sobre los datos
- Alto rendimiento: optimizado para cargas de trabajo intensivas
- Licencia AGPL: uso gratuito en producción

---

## Desarrollo Local

### 1. Levantar MinIO con Docker

```bash
# Desde la carpeta cupido-backend
cd cupido-backend

# Levantar MinIO
docker-compose -f docker-compose.minio.yml up -d
```

### 2. Verificar que MinIO está corriendo

- **API S3:** http://localhost:9000
- **Console Web:** http://localhost:9001
  - Usuario: `minioadmin`
  - Contraseña: `minioadmin`

### 3. Configurar variables de entorno (.env)

```env
# MinIO Local
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=cupido-media
MINIO_USE_SSL=False
MINIO_PUBLIC_URL=http://localhost:9000
```

### 4. Probar la conexión

```bash
# Activar virtualenv
source venv/bin/activate

# Verificar que Django puede conectarse a MinIO
python manage.py shell
```

```python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Subir archivo de prueba
path = default_storage.save('test/hello.txt', ContentFile(b'Hello MinIO!'))
print(f"Archivo guardado en: {path}")

# Verificar que existe
print(f"Existe: {default_storage.exists(path)}")

# Obtener URL
print(f"URL: {default_storage.url(path)}")

# Limpiar
default_storage.delete(path)
```

---

## Producción

### Opción A: MinIO Self-Hosted (Recomendado para control total)

#### 1. Desplegar MinIO en servidor de producción

```bash
# En el servidor de producción (190.90.114.214 u otro)
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=<USUARIO_SEGURO> \
  -e MINIO_ROOT_PASSWORD=<CONTRASEÑA_SEGURA> \
  -v /data/minio:/data \
  --restart unless-stopped \
  minio/minio server /data --console-address ":9001"
```

#### 2. Configurar HTTPS (Importante para producción)

Usar Nginx como reverse proxy con SSL:

```nginx
# /etc/nginx/sites-available/minio
server {
    listen 443 ssl;
    server_name minio.cupidocol.com;

    ssl_certificate /etc/letsencrypt/live/minio.cupidocol.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/minio.cupidocol.com/privkey.pem;

    # Ignorar límite de tamaño para uploads
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name minio-console.cupidocol.com;

    ssl_certificate /etc/letsencrypt/live/minio-console.cupidocol.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/minio-console.cupidocol.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:9001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support para console
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 3. Crear bucket y configurar acceso

```bash
# Instalar mc (MinIO Client)
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configurar alias
mc alias set cupido https://minio.cupidocol.com <USUARIO> <CONTRASEÑA>

# Crear bucket
mc mb cupido/cupido-media

# Hacer bucket público (para servir imágenes directamente)
mc anonymous set public cupido/cupido-media
```

#### 4. Variables de entorno en producción (.env)

```env
# MinIO Producción
MINIO_ENDPOINT=https://minio.cupidocol.com
MINIO_ACCESS_KEY=<USUARIO_SEGURO>
MINIO_SECRET_KEY=<CONTRASEÑA_SEGURA>
MINIO_BUCKET_NAME=cupido-media
MINIO_USE_SSL=True
MINIO_PUBLIC_URL=https://minio.cupidocol.com
```

### Opción B: Usar el mismo servidor (190.90.114.214)

Si prefieres usar el mismo servidor donde está PostgreSQL y Redis:

```bash
# SSH al servidor
ssh usuario@190.90.114.214

# Crear directorio para datos
sudo mkdir -p /data/minio
sudo chown -R 1000:1000 /data/minio

# Ejecutar MinIO
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=cupido_minio_user \
  -e MINIO_ROOT_PASSWORD=<CONTRASEÑA_SEGURA_32_CHARS> \
  -v /data/minio:/data \
  --restart unless-stopped \
  minio/minio server /data --console-address ":9001"
```

Variables de entorno:
```env
MINIO_ENDPOINT=http://190.90.114.214:9000
MINIO_ACCESS_KEY=cupido_minio_user
MINIO_SECRET_KEY=<CONTRASEÑA_SEGURA_32_CHARS>
MINIO_BUCKET_NAME=cupido-media
MINIO_USE_SSL=False
MINIO_PUBLIC_URL=http://190.90.114.214:9000
```

---

## Migración de archivos existentes

Si hay imágenes en `MEDIA_ROOT` local, migrarlas a MinIO:

```bash
# Instalar mc
pip install minio

# Script de migración
python manage.py shell
```

```python
import os
from django.conf import settings
from django.core.files.storage import default_storage
from pathlib import Path

media_root = Path(settings.BASE_DIR) / "media"

for root, dirs, files in os.walk(media_root):
    for filename in files:
        local_path = Path(root) / filename
        relative_path = local_path.relative_to(media_root)
        
        with open(local_path, 'rb') as f:
            default_storage.save(str(relative_path), f)
            print(f"Migrado: {relative_path}")
```

---

## Troubleshooting

### Error: "Could not connect to the endpoint URL"
- Verificar que MinIO está corriendo: `docker ps`
- Verificar endpoint en .env
- Verificar firewall/puertos

### Error: "Access Denied"
- Verificar credenciales (ACCESS_KEY, SECRET_KEY)
- Verificar que el bucket existe
- Verificar permisos del bucket

### Error: "Bucket does not exist"
```bash
# Crear bucket manualmente
mc mb local/cupido-media
```

### Las imágenes no cargan en el frontend
- Verificar `MINIO_PUBLIC_URL` apunta a URL accesible desde el navegador
- Verificar CORS en MinIO si es necesario
- Verificar que el bucket es público o usar URLs firmadas

---

## Arquitectura Final

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│  Django API     │────▶│     MinIO       │
│ (React/Vite)    │     │ (DRF + Storages)│     │  (S3 Storage)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                                               │
        │              Descarga directa                 │
        └───────────────────────────────────────────────┘
```

1. **Upload:** Frontend → Django API → MinIO
2. **Download:** Frontend → MinIO (directo, bucket público)

---

## Seguridad (Checklist para Producción)

- [ ] Cambiar credenciales por defecto (minioadmin)
- [ ] Habilitar HTTPS/TLS
- [ ] Configurar firewall (solo puertos necesarios)
- [ ] Usar credenciales en variables de entorno (no hardcoded)
- [ ] Configurar backups periódicos de /data/minio
- [ ] Monitorear espacio en disco
- [ ] Configurar lifecycle policies si es necesario (borrado automático)
