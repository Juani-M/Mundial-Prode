import sys
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Añadir el backend al path para poder importar módulos de la app y la configuración de DB
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import SessionLocal
from app.models.match import Match

# --- CONFIGURACIÓN ---
# Cargar variables de entorno desde el archivo .env del backend
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
# URL para obtener los partidos del Mundial (todos los partidos del torneo)
URL = "https://api.football-data.org/v4/competitions/WC/matches"

HEADERS = {
    "X-Auth-Token": API_KEY
}

# Diccionario simple de traducción de nombres de equipos
TRADUCCIONES = {
    "Qatar": "Qatar",
    "Ecuador": "Ecuador",
    "Senegal": "Senegal",
    "Netherlands": "Países Bajos",
    "England": "Inglaterra",
    "Iran": "Irán",
    "United States": "Estados Unidos",
    "Wales": "Gales",
    "Argentina": "Argentina",
    "Saudi Arabia": "Arabia Saudita",
    "Mexico": "México",
    "Poland": "Polonia",
    "France": "Francia",
    "Australia": "Australia",
    "Denmark": "Dinamarca",
    "Tunisia": "Túnez",
    "Spain": "España",
    "Costa Rica": "Costa Rica",
    "Germany": "Alemania",
    "Japan": "Japón",
    "Belgium": "Bélgica",
    "Canada": "Canadá",
    "Morocco": "Marruecos",
    "Croatia": "Croacia",
    "Brazil": "Brasil",
    "Serbia": "Serbia",
    "Switzerland": "Suiza",
    "Cameroon": "Camerún",
    "Portugal": "Portugal",
    "Ghana": "Ghana",
    "Uruguay": "Uruguay",
    "South Korea": "Corea del Sur"
}

def traducir_equipo(nombre):
    return TRADUCCIONES.get(nombre, nombre)

def formatear_grupo(group_string):
    # Transforma "GROUP_A" en "Grupo A"
    if not group_string or "GROUP" not in group_string:
        return group_string
    letra = group_string.split("_")[-1]
    return f"Grupo {letra}"

def main():
    if API_KEY == "TU_API_KEY_AQUI":
        print("Error: Debes insertar tu API_KEY en el script antes de ejecutarlo.")
        return

    print("Obteniendo partidos de football-data.org...")
    response = requests.get(URL, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error al obtener datos: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    matches_data = data.get("matches", [])
    
    db = SessionLocal()
    nuevos_partidos = 0
    
    try:
        for m in matches_data:
            # Solo iteramos sobre la fase de grupos para este script
            if m.get("stage") != "GROUP_STAGE":
                continue
                
            home_team_name = m.get("homeTeam", {}).get("name")
            away_team_name = m.get("awayTeam", {}).get("name")
            
            if not home_team_name or not away_team_name:
                continue
                
            team_home_es = traducir_equipo(home_team_name)
            team_away_es = traducir_equipo(away_team_name)
            
            match_date_str = m.get("utcDate") # ej: "2022-11-20T16:00:00Z"
            # Convertir string UTC a objeto datetime
            match_date = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%SZ")
            
            fase_grupo = formatear_grupo(m.get("group"))
            
            # Verificar si ya existe para evitar duplicados al correr el script varias veces
            existente = db.query(Match).filter(
                Match.team_home == team_home_es,
                Match.team_away == team_away_es,
                Match.phase == fase_grupo
            ).first()
            
            if not existente:
                nuevo_partido = Match(
                    team_home=team_home_es,
                    team_away=team_away_es,
                    match_date=match_date,
                    phase=fase_grupo,
                    status="pending"
                )
                db.add(nuevo_partido)
                nuevos_partidos += 1
                
        db.commit()
        print(f"¡Éxito! Se han guardado {nuevos_partidos} partidos de la fase de grupos en la base de datos local.")
    except Exception as e:
        db.rollback()
        print(f"Ocurrió un error al guardar en BD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
