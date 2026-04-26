import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import Base, engine
import app.models  # noqa: F401 — registra todos los modelos en Base.metadata
from app.workers.update_results import update_match_results
from app.workers.fetch_fixtures import fetch_and_sync_fixtures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Scheduler de fondo ───────────────────────────────────────────────────────
scheduler = BackgroundScheduler(daemon=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear tablas y arrancar scheduler
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas verificadas/creadas.")

    scheduler.add_job(
        fetch_and_sync_fixtures,
        "interval",
        hours=1,
        id="fetch_fixtures",
        replace_existing=True,
    )
    scheduler.add_job(
        update_match_results,
        "interval",
        minutes=5,
        id="update_results",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler iniciado: fixture (cada 1h), resultados (cada 5min).")

    yield  # App corriendo

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Scheduler detenido.")


# ── Importar routers ─────────────────────────────────────────────────────────
from app.api.users import router as users_router
from app.api.matches import router as matches_router
from app.api.predictions import router as predictions_router
from app.api.group_predictions import router as group_predictions_router
from app.api.auth import router as auth_router

# ── App FastAPI ───────────────────────────────────────────────────────────────
app = FastAPI(title="API Prode Mundial", version="1.0", lifespan=lifespan)

FRONTEND_URL = os.getenv("FRONTEND_URL", "")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://orange-plant-0e03b000f.7.azurestaticapps.net",  # Azure Static Web App
]

if FRONTEND_URL and FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(matches_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(group_predictions_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "estado": "Online",
        "mensaje": "¡El motor del Prode está vivo y esperando el pitazo inicial!",
    }


@app.post("/api/v1/admin/update-now")
def trigger_update():
    """Dispara manualmente la actualización de resultados (útil para testing)."""
    update_match_results()
    return {"message": "Actualización de resultados ejecutada."}


@app.post("/api/v1/admin/sync-fixtures")
def trigger_sync():
    """Dispara manualmente la sincronización del fixture (útil para testing)."""
    fetch_and_sync_fixtures()
    return {"message": "Sincronización de fixture ejecutada."}
