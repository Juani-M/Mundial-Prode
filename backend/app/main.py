from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
import app.models  # noqa: F401 — registra todos los modelos en Base.metadata

# Crea las tablas en SQLite si aún no existen
Base.metadata.create_all(bind=engine)

from app.api.users import router as users_router
from app.api.matches import router as matches_router
from app.api.predictions import router as predictions_router
from app.api.group_predictions import router as group_predictions_router
from app.api.auth import router as auth_router

app = FastAPI(title="API Prode Mundial", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "mensaje": "¡El motor del Prode está vivo y esperando el pitazo inicial!"
    }
