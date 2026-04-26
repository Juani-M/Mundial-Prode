"""
seed_matches.py — Carga el fixture completo del Mundial 2026 desde football-data.org.
Ejecutar UNA SOLA VEZ antes del torneo (o para resetear la BD limpia).

Uso:
    cd j:\\Proyectos\\prode
    $env:DATABASE_URL = "postgresql://..."   # opcional si ya está en backend/.env
    python seed_matches.py
"""
import sys
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# Añadir el backend al path para poder importar módulos de la app
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Cargar .env del backend
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

from app.core.database import SessionLocal, Base, engine  # noqa: E402
from app.models.match import Match  # noqa: E402
import app.models  # noqa: F401, E402 — registra todos los modelos

# --- CONFIGURACIÓN ---
API_KEY = os.getenv("SPORTS_API_KEY") or os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = os.getenv("SPORTS_API_BASE_URL", "https://api.football-data.org/v4")
COMPETITION_CODE = "WC"

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

PHASE_MAP = {
    "ROUND_OF_32":    "16avos",
    "ROUND_OF_16":    "Octavos",
    "QUARTER_FINALS": "Cuartos",
    "SEMI_FINALS":    "Semifinal",
    "THIRD_PLACE":    "Tercer Puesto",
    "FINAL":          "Final",
}


def traducir(nombre: str) -> str:
    return TRADUCCIONES.get(nombre, nombre)


def formatear_grupo(group_string: str | None) -> str:
    if not group_string or "GROUP" not in group_string:
        return group_string or "Grupos"
    letra = group_string.split("_")[-1]
    return f"Grupo {letra}"


def main():
    if not API_KEY:
        print("❌ Error: Falta SPORTS_API_KEY en backend/.env")
        print("   Registrate en https://www.football-data.org/client/register")
        return

    print(f"🌐 Consultando football-data.org — competencia: {COMPETITION_CODE}...")
    response = requests.get(
        f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches",
        headers={"X-Auth-Token": API_KEY},
        timeout=15,
    )

    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text[:300]}")
        return

    data = response.json()
    api_matches = data.get("matches", [])
    print(f"✅ {len(api_matches)} partidos recibidos de la API.")

    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    insertados = 0
    saltados = 0

    try:
        # Limpiar partidos existentes para partir de cero limpio
        confirm = input("\n⚠️  Esto BORRARÁ todos los partidos actuales. ¿Continuar? (s/N): ").strip().lower()
        if confirm != "s":
            print("Cancelado.")
            return

        db.query(Match).delete()
        db.commit()
        print("🗑️  Partidos anteriores eliminados.")

        for m in api_matches:
            external_id = m.get("id")
            stage = m.get("stage", "GROUP_STAGE")

            home_api = m.get("homeTeam", {}).get("name", "")
            away_api = m.get("awayTeam", {}).get("name", "")

            # Ignorar partidos TBD (fases eliminatorias sin equipos definidos aún)
            if not home_api or not away_api:
                saltados += 1
                continue

            team_home = traducir(home_api)
            team_away = traducir(away_api)

            if stage == "GROUP_STAGE":
                phase = formatear_grupo(m.get("group"))
            else:
                phase = PHASE_MAP.get(stage, stage)

            date_str = m.get("utcDate", "")
            try:
                match_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                print(f"  ⚠️  Fecha inválida para partido {external_id}: {date_str}")
                saltados += 1
                continue

            nuevo = Match(
                external_id=external_id,
                team_home=team_home,
                team_away=team_away,
                match_date=match_date,
                phase=phase,
                status="pending",
            )
            db.add(nuevo)
            insertados += 1

        db.commit()
        print(f"\n🎉 Seed completo: {insertados} partidos insertados, {saltados} omitidos (TBD).")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al guardar: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
