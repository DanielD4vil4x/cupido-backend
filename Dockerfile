FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Ejecutar migraciones automáticamente antes de iniciar
CMD ["bash", "-c", "python manage.py migrate --fake && python manage.py runserver 0.0.0.0:8000"]
