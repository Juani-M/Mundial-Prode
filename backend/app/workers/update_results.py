"""
Worker: update_results.py
Consulta la API de football-data.org cada N minutos,
detecta partidos finalizados o en curso, actualiza la BD
y calcula los puntos de todas las predicciones asociadas.
"""
import logging
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.match import Match
from app.models.prediction import Prediction
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)

COMPETITION_CODE = "WC"

# Mapeo de estados de la API a los estados internos de la app
API_STATUS_MAP = {
    "FINISHED":   "finished",
    "IN_PLAY":    "in_progress",
    "PAUSED":     "in_progress",
    "SUSPENDED":  "in_progress",
    "SCHEDULED":  "pending",
    "TIMED":      "pending",
    "POSTPONED":  "pending",
    "CANCELLED":  "pending",
}

# Mapeo de fases de la API a las fases internas
PHASE_MAP = {
    "GROUP_STAGE":    None,       # Se calcula con el grupo (ej: "Grupo A")
    "ROUND_OF_32":    "16avos",   # 2026 WC tiene ronda de 32
    "ROUND_OF_16":    "Octavos",
    "QUARTER_FINALS": "Cuartos",
    "SEMI_FINALS":    "Semifinal",
    "THIRD_PLACE":    "Tercer Puesto",
    "FINAL":          "Final",
}


def _calcular_puntos(db: Session, match: Match) -> None:
    """Calcula y asigna puntos a todas las predicciones de un partido finalizado."""
    predictions = db.query(Prediction).filter(Prediction.match_id == match.id).all()

    if not predictions:
        return

    # Tendencia real del partido
    if match.score_home_actual > match.score_away_actual:
        tendencia_real = 1
    elif match.score_home_actual < match.score_away_actual:
        tendencia_real = -1
    else:
        tendencia_real = 0

    for pred in predictions:
        if pred.points_earned is not None:
            continue  # Ya calculado, no recalcular

        # Resultado exacto → 2 puntos
        if (pred.score_home_predicted == match.score_home_actual and
                pred.score_away_predicted == match.score_away_actual):
            puntos = 2
        else:
            # Solo acertó la tendencia → 1 punto
            if pred.score_home_predicted > pred.score_away_predicted:
                tendencia_pred = 1
            elif pred.score_home_predicted < pred.score_away_predicted:
                tendencia_pred = -1
            else:
                tendencia_pred = 0

            puntos = 1 if tendencia_pred == tendencia_real else 0

        pred.points_earned = puntos

        # Acumular puntos al usuario
        user = db.query(Usuario).filter(Usuario.id == pred.user_id).first()
        if user:
            user.total_points += puntos

    logger.info(f"[update_results] Puntos calculados para partido {match.id} "
                f"({match.team_home} {match.score_home_actual} - "
                f"{match.score_away_actual} {match.team_away})")


def update_match_results() -> None:
    """
    Punto de entrada del worker. Descarga los partidos del Mundial desde
    football-data.org y sincroniza estado y resultados en la BD.
    """
    if not settings.SPORTS_API_KEY:
        logger.warning("[update_results] SPORTS_API_KEY no configurada. Worker omitido.")
        return

    logger.info("[update_results] Consultando API de football-data.org...")

    try:
        response = requests.get(
            f"{settings.SPORTS_API_BASE_URL}/competitions/{COMPETITION_CODE}/matches",
            headers={"X-Auth-Token": settings.SPORTS_API_KEY},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"[update_results] Error al consultar la API: {e}")
        return

    data = response.json()
    api_matches = data.get("matches", [])
    logger.info(f"[update_results] {len(api_matches)} partidos recibidos de la API.")

    db: Session = SessionLocal()
    actualizados = 0

    try:
        for api_match in api_matches:
            external_id = api_match.get("id")
            if not external_id:
                continue

            # Buscar en la BD por external_id (primario) o por nombres de equipo (fallback)
            match = db.query(Match).filter(Match.external_id == external_id).first()

            if not match:
                # Fallback: intentar por nombres de equipo
                home_name = api_match.get("homeTeam", {}).get("name", "")
                away_name = api_match.get("awayTeam", {}).get("name", "")
                match = db.query(Match).filter(
                    Match.team_home == home_name,
                    Match.team_away == away_name,
                ).first()
                # Si lo encontramos así, guardamos el external_id para futuras consultas
                if match:
                    match.external_id = external_id

            if not match:
                continue  # Partido no seeded todavía

            api_status = api_match.get("status", "")
            nuevo_estado = API_STATUS_MAP.get(api_status, "pending")

            score_full = api_match.get("score", {}).get("fullTime", {})
            score_home = score_full.get("home")
            score_away = score_full.get("away")

            # — Partido finalizado —
            if nuevo_estado == "finished" and match.status != "finished":
                if score_home is not None and score_away is not None:
                    match.score_home_actual = score_home
                    match.score_away_actual = score_away
                    match.status = "finished"
                    _calcular_puntos(db, match)
                    actualizados += 1

            # — Partido en curso —
            elif nuevo_estado == "in_progress" and match.status != "finished":
                match.status = "in_progress"
                if score_home is not None:
                    match.score_home_actual = score_home
                if score_away is not None:
                    match.score_away_actual = score_away

        db.commit()
        logger.info(f"[update_results] Sincronización completa. "
                    f"Partidos finalizados actualizados: {actualizados}.")

    except Exception as e:
        db.rollback()
        logger.error(f"[update_results] Error al actualizar la BD: {e}", exc_info=True)
    finally:
        db.close()
