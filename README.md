# Cupido Backend

Backend API desarrollada con **Django** y **Django REST Framework (DRF)** para el proyecto cUPido.  
Su arquitectura está diseñada para ofrecer una base escalable, modular y segura, con integración a PostgreSQL y Redis.

---

## Estructura de ramas

| Rama | Propósito |
|------|------------|
| `main` | Versión estable, siempre lista para despliegue. |
| `develop` | Rama de integración continua donde se fusionan las *features* completas. |
| `feature/*` | Ramas de desarrollo de funcionalidades individuales (por ejemplo: `feature/auth`, `feature/swipe`). |

---

## Requisitos

Antes de comenzar, asegúrate de tener instalado:

| Herramienta | Versión mínima recomendada |
|--------------|-----------------------------|
| Python | 3.11+ |
| PostgreSQL | **16.10** |
| Docker | Última versión estable |
| Virtualenv | Recomendado para entornos locales |

---

## ⚙️ Tecnologías principales

- **Django** + **Django REST Framework**
- **PostgreSQL 16.10**
- **Redis** (para cache y validaciones temporales)
- **Docker** (para el manejo de servicios)
- **SingleJWT** (autenticación segura basada en tokens)
- **Axios** (para consumo desde el frontend)
- **reCAPTCHA** (protección en endpoints críticos)

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/cUPido-App/cupido-backend.git
cd cupido-backend
python -m venv venv
source venv/bin/activate  # En Linux / Mac
venv\Scripts\activate     # En Windows
pip install -r requirements.txt 
cd ..
python manage.py runserver

