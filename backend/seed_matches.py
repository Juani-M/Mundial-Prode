import sys
from datetime import datetime

# Asegurar que la carpeta backend esté en el path para importar 'app'
sys.path.append(".")

from app.core.database import SessionLocal
from app.models.match import Match

def seed():
    db = SessionLocal()
    
    # Limpiar partidos anteriores de prueba (opcional, pero útil)
    db.query(Match).delete()
    db.commit()

    # Partido 1: Pendiente
    match1 = Match(
        team_home="Argentina",
        team_away="Polonia",
        match_date=datetime.now(),
        phase="Grupos",
        status="pending"
    )

    # Partido 2: En curso
    match2 = Match(
        team_home="Brasil",
        team_away="Suiza",
        match_date=datetime.now(),
        phase="Grupos",
        status="in_progress",
        score_home_actual=1,
        score_away_actual=0
    )

    # Partido 3: Finalizado
    match3 = Match(
        team_home="España",
        team_away="Alemania",
        match_date=datetime.now(),
        phase="Grupos",
        status="finished",
        score_home_actual=1,
        score_away_actual=1
    )

    db.add_all([match1, match2, match3])
    db.commit()
    db.close()
    print("3 partidos de prueba agregados exitosamente a la base de datos.")

if __name__ == "__main__":
    seed()
