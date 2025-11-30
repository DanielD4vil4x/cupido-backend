# Image Upload Feature (Backend)

Submodulo de `profile_app` que gestiona la subida, almacenamiento y administracion de imagenes de perfil de los usuarios.

## Tabla de Contenidos

1. [Descripcion General](#descripcion-general)
2. [Arquitectura](#arquitectura)
3. [Modelo de Datos](#modelo-de-datos)
4. [API Endpoints](#api-endpoints)
5. [Almacenamiento con MinIO](#almacenamiento-con-minio)
6. [Configuracion](#configuracion)
7. [Desarrollo Local](#desarrollo-local)
8. [Validaciones](#validaciones)
9. [Tests](#tests)

---

## Descripcion General

Este modulo permite a los usuarios autenticados:

- Subir hasta 3 imagenes de perfil
- Establecer una imagen como principal
- Eliminar imagenes existentes
- Listar sus imagenes actuales

Las imagenes se almacenan en MinIO (servidor S3-compatible) para escalabilidad y portabilidad entre ambientes de desarrollo y produccion.

---

## Arquitectura

```
imageUpload/
    __init__.py
    models.py        # Modelo Imagen con logica de renombrado y storage
    serializers.py   # Validacion de tipo/tamano de archivos
    views.py         # Endpoints REST (ListCreate, RetrieveUpdateDestroy)
    urls.py          # Rutas: /profile/photos/
    tests.py         # Tests unitarios con storage temporal
    migrations/      # Migraciones de base de datos
```

### Dependencias

- `django-storages[boto3]`: Abstraccion de storage compatible con S3/MinIO
- `boto3`: SDK de AWS para comunicacion con MinIO
- `Pillow`: Procesamiento de imagenes

---

## Modelo de Datos

### Tabla: `Imagen`

| Campo         | Tipo           | Descripcion                                      |
|---------------|----------------|--------------------------------------------------|
| id            | AutoField      | Identificador unico (PK)                         |
| usuario       | ForeignKey     | Referencia al usuario propietario                |
| imagen        | ImageField     | Ruta del archivo en MinIO                        |
| es_principal  | BooleanField   | Indica si es la imagen principal del usuario     |
| fecha_subida  | DateTimeField  | Timestamp de creacion                            |

### Logica de Negocio en el Modelo

1. **Renombrado automatico**: Al guardar, el archivo temporal se renombra con el formato:
   ```
   usuarios/{usuario_id}/{usuario_id}_imagen_{imagen_id}.{ext}
   ```

2. **Imagen principal unica**: Al establecer `es_principal=True`, se desmarca automaticamente cualquier otra imagen principal del mismo usuario.

3. **Eliminacion en cascada**: Al eliminar el registro, se elimina tambien el archivo fisico de MinIO.

---

## API Endpoints

Base URL: `/api/profile/photos/`

### Listar imagenes del usuario

```
GET /api/profile/photos/
Authorization: Bearer <token>

Response 200:
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "usuario": 5,
      "imagen": "http://localhost:9000/cupido-media/usuarios/5/5_imagen_1.jpg",
      "es_principal": true,
      "fecha_subida": "2025-11-27T10:30:00Z"
    },
    ...
  ]
}
```

### Subir imagen

```
POST /api/profile/photos/
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
  imagen: <archivo binario>

Response 201:
{
  "id": 3,
  "usuario": 5,
  "imagen": "http://localhost:9000/cupido-media/usuarios/5/5_imagen_3.jpg",
  "es_principal": false,
  "fecha_subida": "2025-11-27T12:00:00Z"
}

Response 400 (limite alcanzado):
{
  "detail": "Has alcanzado el maximo de 3 imagenes permitidas."
}
```

### Obtener imagen especifica

```
GET /api/profile/photos/{id}/
Authorization: Bearer <token>

Response 200:
{
  "id": 1,
  "usuario": 5,
  "imagen": "http://localhost:9000/cupido-media/usuarios/5/5_imagen_1.jpg",
  "es_principal": true,
  "fecha_subida": "2025-11-27T10:30:00Z"
}
```

### Establecer imagen principal

```
PATCH /api/profile/photos/{id}/
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "es_principal": true
}

Response 200:
{
  "id": 2,
  "es_principal": true,
  ...
}
```

### Eliminar imagen

```
DELETE /api/profile/photos/{id}/
Authorization: Bearer <token>

Response 204: No Content
```

---

## Almacenamiento con MinIO

MinIO es un servidor de almacenamiento de objetos compatible con la API de Amazon S3. Se utiliza como backend de storage para las imagenes de perfil.

### Ventajas

- **Portabilidad**: Mismo codigo funciona con MinIO local, AWS S3 o cualquier storage S3-compatible
- **Escalabilidad**: Almacenamiento distribuido sin limite de archivos
- **Independencia**: Los archivos no estan en el filesystem del servidor Django

### Estructura de archivos en MinIO

```
cupido-media/                    # Bucket
    usuarios/
        {usuario_id}/
            {usuario_id}_imagen_{imagen_id}.jpg
            {usuario_id}_imagen_{imagen_id}.png
```

### Configuracion de Django Storages

El proyecto utiliza `django-storages` con el backend `S3Boto3Storage`. La configuracion se encuentra en `config/settings.py`:

```python
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": MINIO_ACCESS_KEY,
            "secret_key": MINIO_SECRET_KEY,
            "bucket_name": MINIO_BUCKET_NAME,
            "endpoint_url": MINIO_ENDPOINT,
            "addressing_style": "path",
            "signature_version": "s3v4",
        },
    },
}
```

---

## Configuracion

### Variables de Entorno

| Variable              | Descripcion                                   | Valor por defecto      |
|-----------------------|-----------------------------------------------|------------------------|
| MINIO_ENDPOINT        | URL del servidor MinIO                        | http://localhost:9000  |
| MINIO_ACCESS_KEY      | Credencial de acceso                          | (requerido)            |
| MINIO_SECRET_KEY      | Credencial secreta                            | (requerido)            |
| MINIO_BUCKET_NAME     | Nombre del bucket                             | cupido-media           |
| MINIO_USE_SSL         | Usar HTTPS                                    | False                  |
| MINIO_PUBLIC_URL      | URL publica para servir archivos              | (igual a ENDPOINT)     |
| PHOTO_MAX_UPLOAD_SIZE | Tamano maximo en bytes                        | 5242880 (5MB)          |
| PHOTO_MAX_FILES       | Numero maximo de fotos por usuario            | 3                      |

---

## Desarrollo Local

### Requisitos previos

1. Docker instalado y corriendo
2. Python 3.10+ con virtualenv activado

### Pasos

1. **Levantar MinIO con Docker**:
   ```bash
   cd cupido-backend
   sudo docker-compose -f docker-compose.minio.yml up -d
   ```

2. **Verificar que el bucket se creo**:
   ```bash
   sudo docker logs cupido-minio-setup
   # Deberia mostrar: "Bucket cupido-media creado y configurado como publico"
   ```

3. **Acceder a la consola web de MinIO**:
   - URL: http://localhost:9001
   - Usuario: minioadmin
   - Password: minioadmin

4. **Configurar variables de entorno**:
   Asegurar que el archivo `.env` contenga:
   ```env
   MINIO_ENDPOINT=http://localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET_NAME=cupido-media
   ```

5. **Ejecutar migraciones** (si es necesario):
   ```bash
   python manage.py migrate
   ```

6. **Probar la subida**:
   ```bash
   python manage.py shell
   >>> from django.core.files.storage import default_storage
   >>> default_storage.save('test.txt', ContentFile(b'hello'))
   'test.txt'
   >>> default_storage.exists('test.txt')
   True
   >>> default_storage.delete('test.txt')
   ```

---

## Validaciones

El serializer implementa las siguientes validaciones:

### Tipo de archivo

Solo se aceptan:
- `image/jpeg`
- `image/png`
- `image/webp`

### Tamano maximo

Por defecto 5MB, configurable via `PHOTO_MAX_UPLOAD_SIZE`.

### Limite de imagenes

Por defecto 3 imagenes por usuario, configurable via `PHOTO_MAX_FILES`.

### Codigos de error

| Codigo | Mensaje                                              |
|--------|------------------------------------------------------|
| 400    | El archivo debe ser una imagen (jpeg, png, webp).    |
| 400    | La imagen excede el tamano maximo de 5MB.            |
| 400    | Has alcanzado el maximo de 3 imagenes permitidas.    |
| 401    | No autenticado                                       |
| 404    | Imagen no encontrada                                 |

---

## Tests

Los tests utilizan `@override_settings` para usar un storage temporal de filesystem, evitando dependencia de MinIO durante CI/CD.

### Ejecutar tests

```bash
python manage.py test apps.profile_app.subapps.imageUpload
```

### Casos de prueba

| Test                         | Descripcion                                          |
|------------------------------|------------------------------------------------------|
| test_upload_image_success    | Subida exitosa de imagen valida                      |
| test_upload_non_image_failure| Rechazo de archivo que no es imagen                  |
| test_max_images_limit        | Limite de 3 imagenes por usuario                     |
| test_principal_image_toggle  | Solo una imagen principal por usuario                |
| test_delete_image            | Eliminacion de imagen y archivo fisico               |

---

## Servicios de Procesamiento

El modulo incluye servicios especializados en `services/` para el procesamiento de imagenes:

### ImageProcessor (`services/image_processor.py`)

Servicio de compresion automatica de imagenes para optimizar almacenamiento y carga.

**Caracteristicas:**
- Limite objetivo: 400KB por imagen
- Reduccion progresiva de calidad (de 85% a 40%)
- Conversion automatica a JPEG para mejor compresion
- Reduccion de dimensiones si la imagen es muy grande (max 1920px)

**Flujo de compresion:**
```
1. Si imagen > 400KB, aplicar compresion progresiva
2. Reducir calidad de 85% a 40% en pasos de 10%
3. Si aun excede, redimensionar a max 1920px de ancho
4. Si aun excede, forzar 1280px con calidad minima
```

### ContentModerator (`services/content_moderator.py`)

Servicio de moderacion de contenido usando la API de Sightengine.

**Categorias moderadas:**
| Categoria | Descripcion | Umbral |
|-----------|-------------|--------|
| `nudity` | Desnudez parcial o total | 0.5 |
| `weapon` | Armas de fuego o blancas | 0.5 |
| `drugs` | Drogas o parafernalia | 0.5 |
| `gore` | Violencia grafica | 0.5 |

**Politica de fallos (Fail-Open):**
- Si la API de Sightengine falla o no esta configurada, la imagen se **ACEPTA**.
- Esto evita bloquear usuarios por problemas tecnicos externos.

**Configuracion requerida (.env):**
```env
SIGHTENGINE_API_USER=<tu_api_user>
SIGHTENGINE_API_SECRET=<tu_api_secret>
```

**Ejemplo de respuesta de rechazo:**
```json
{
  "imagen": [
    "Esta imagen no puede ser aceptada porque contiene: armas o elementos peligrosos. Por favor, sube una imagen diferente."
  ]
}
```

---

## Endpoint de Status

El endpoint `/api/v1/profile/images/status/` permite verificar si un usuario cumple con los requisitos minimos de fotos.

**Request:**
```bash
curl -X GET https://backend.cupidocol.com/api/v1/profile/images/status/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "has_minimum": true,
  "current_count": 2,
  "minimum_required": 1,
  "maximum_allowed": 3,
  "can_upload_more": true
}
```

---

## Notas de Produccion

1. **Credenciales**: En produccion, usar credenciales seguras distintas a las de desarrollo.

2. **HTTPS**: Configurar `MINIO_USE_SSL=True` y asegurar que MinIO tenga certificado SSL.

3. **Bucket privado**: Considerar usar `querystring_auth=True` para URLs firmadas si el contenido debe ser privado.

4. **CDN**: Para mejor rendimiento, configurar `MINIO_PUBLIC_URL` apuntando a un CDN.

5. **Backup**: Configurar politicas de backup en MinIO para los datos del bucket.

6. **Sightengine**: Configurar las variables `SIGHTENGINE_API_USER` y `SIGHTENGINE_API_SECRET` para habilitar la moderacion de contenido.

---

## Changelog

- **v1.1.0** (Nov 2024): Agregados servicios de procesamiento
  - Compresion automatica de imagenes (<=400KB)
  - Moderacion de contenido con Sightengine
  - Endpoint de status para validacion de registro
  
- **v1.0.0**: Implementacion inicial
  - Almacenamiento en MinIO
  - CRUD de imagenes de perfil
