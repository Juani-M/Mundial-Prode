# 🏆 Prode — Juego de Pronósticos Deportivos

Aplicación web full-stack para gestionar pronósticos deportivos (tipo Prode).

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Base de datos | PostgreSQL 16 + SQLAlchemy 2 |
| Frontend | Vanilla JS (ES6) + HTML5 + CSS3 |
| Infraestructura | Docker + Docker Compose + Nginx |

## Estructura del Proyecto

```
prode/
├── backend/        # API REST (FastAPI)
│   └── app/
│       ├── api/        # Endpoints por dominio
│       ├── models/     # Modelos ORM (SQLAlchemy)
│       ├── schemas/    # Validación Pydantic
│       ├── services/   # Lógica de negocio
│       ├── workers/    # Tareas en background (APIs externas)
│       └── core/       # Config, DB, seguridad
├── frontend/       # SPA estática (Vanilla JS)
├── nginx/          # Reverse proxy
└── docker-compose.yml
```

## Inicio Rápido

### 1. Clonar y configurar variables de entorno
```bash
git clone <repo-url>
cd prode
cp .env.example .env
# Editar .env con tus valores reales
```

### 2. Levantar todos los servicios
```bash
docker compose up --build
```

### 3. Acceder
- **Frontend**: http://localhost
- **API (docs)**: http://localhost/docs
- **API directa**: http://localhost:8000

## Servicios Docker

| Servicio | Puerto | Descripción |
|---|---|---|
| `db` | 5432 | PostgreSQL |
| `backend` | 8000 | FastAPI (uvicorn) |
| `worker` | — | Worker de tareas en background |
| `nginx` | 80 | Servidor web + reverse proxy |

## Desarrollo Local (sin Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```
