"""
Worker: fetch_fixtures.py
Descarga el fixture completo del Mundial desde football-data.org
y lo guarda en la BD. Se ejecuta al iniciar la app y periódicamente
para incorporar nuevos partidos de fases eliminatorias.
"""
import logging
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.match import Match

logger = logging.getLogger(__name__)

COMPETITION_CODE = "WC"

# Traducciones de nombres de equipos (inglés API → español app)
TRADUCCIONES = {
    "Argentina": "Argentina",
    "Australia": "Australia",
    "Belgium": "Bélgica",
    "Bolivia": "Bolivia",
    "Brazil": "Brasil",
    "Cameroon": "Camerún",
    "Canada": "Canadá",
    "Chile": "Chile",
    "Colombia": "Colombia",
    "Costa Rica": "Costa Rica",
    "Croatia": "Croacia",
    "Denmark": "Dinamarca",
    "DR Congo": "Congo DR",
    "Ecuador": "Ecuador",
    "Egypt": "Egypt",
    "England": "Inglaterra",
    "France": "Francia",
    "Germany": "Alemania",
    "Ghana": "Ghana",
    "Iran": "Irán",
    "Iraq": "Iraq",
    "Italy": "Italy",
    "Japan": "Japón",
    "Jordan": "Jordan",
    "Korea Republic": "Corea del Sur",
    "Mexico": "México",
    "Morocco": "Marruecos",
    "Netherlands": "Países Bajos",
    "New Zealand": "New Zealand",
    "Norway": "Norway",
    "Panama": "Panama",
    "Paraguay": "Paraguay",
    "Peru": "Peru",
    "Poland": "Polonia",
    "Portugal": "Portugal",
    "Qatar": "Qatar",
    "Saudi Arabia": "Arabia Saudita",
    "Senegal": "Senegal",
    "Serbia": "Serbia",
    "South Korea": "Corea del Sur",
    "Spain": "España",
    "Switzerland": "Suiza",
    "Tunisia": "Túnez",
    "Turkey": "Turkey",
    "United States": "Estados Unidos",
    "Uruguay": "Uruguay",
    "Uzbekistan": "Uzbekistan",
    "Venezuela": "Venezuela",
    "Wales": "Gales",
}

# Mapeo de fases API → fases internas (2026 WC tiene ronda de 32)
PHASE_MAP = {
    "ROUND_OF_32":    "16avos",
    "ROUND_OF_16":    "Octavos",
    "QUARTER_FINALS": "Cuartos",
    "SEMI_FINALS":    "Semifinal",
    "THIRD_PLACE":    "Tercer Puesto",
    "FINAL":          "Final",
}


def _traducir(nombre: str) -> str:
    return TRADUCCIONES.get(nombre, nombre)


def _formatear_grupo(group_string: str | None) -> str:
    """Convierte 'GROUP_A' → 'Grupo A'."""
    if not group_string or "GROUP" not in group_string:
        return group_string or "Grupos"
    letra = group_string.split("_")[-1]
    return f"Grupo {letra}"


def fetch_and_sync_fixtures() -> None:
    """
    Descarga el fixture completo del Mundial y sincroniza con la BD.
    - Los partidos nuevos se insertan.
    - Los existentes (por external_id) se actualizan si cambia la fecha.
    """
    if not settings.SPORTS_API_KEY:
        logger.warning("[fetch_fixtures] SPORTS_API_KEY no configurada. Worker omitido.")
        return

    logger.info("[fetch_fixtures] Descargando fixture del Mundial...")

    try:
        response = requests.get(
            f"{settings.SPORTS_API_BASE_URL}/competitions/{COMPETITION_CODE}/matches",
            headers={"X-Auth-Token": settings.SPORTS_API_KEY},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"[fetch_fixtures] Error al consultar la API: {e}")
        return

    data = response.json()
    api_matches = data.get("matches", [])
    logger.info(f"[fetch_fixtures] {len(api_matches)} partidos recibidos.")

    db: Session = SessionLocal()
    insertados = 0
    actualizados = 0

    try:
        for m in api_matches:
            external_id = m.get("id")
            if not external_id:
                continue

            stage = m.get("stage", "GROUP_STAGE")
            if stage == "GROUP_STAGE":
                phase = _formatear_grupo(m.get("group"))
            else:
                phase = PHASE_MAP.get(stage, stage)

            home_api = m.get("homeTeam", {}).get("name", "")
            away_api = m.get("awayTeam", {}).get("name", "")

            # Ignorar partidos con equipos TBD (fases eliminatorias no definidas aún)
            if not home_api or not away_api:
                continue

            team_home = _traducir(home_api)
            team_away = _traducir(away_api)

            date_str = m.get("utcDate", "")
            try:
                match_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                logger.warning(f"[fetch_fixtures] Fecha inválida para partido {external_id}: {date_str}")
                continue

            existing = db.query(Match).filter(Match.external_id == external_id).first()

            if existing:
                # Actualizar fecha si cambió (partidos reprogramados)
                if existing.match_date != match_date:
                    existing.match_date = match_date
                    actualizados += 1
            else:
                new_match = Match(
                    external_id=external_id,
                    team_home=team_home,
                    team_away=team_away,
                    match_date=match_date,
                    phase=phase,
                    status="pending",
                )
                db.add(new_match)
                insertados += 1

        db.commit()
        logger.info(
            f"[fetch_fixtures] Sincronización completa. "
            f"Insertados: {insertados}, Actualizados: {actualizados}."
        )

    except Exception as e:
        db.rollback()
        logger.error(f"[fetch_fixtures] Error al guardar en BD: {e}", exc_info=True)
    finally:
        db.close()
