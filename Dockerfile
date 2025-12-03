FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn[gevent]

COPY . .

EXPOSE 8000

# Workers asíncronos optimizados
CMD ["bash", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 8 --worker-class gevent --worker-connections 1000 --timeout 120"]
