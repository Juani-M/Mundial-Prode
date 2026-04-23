import sys
sys.path.append(".")
from app.core.database import SessionLocal
from app.models.prediction import Prediction
from app.models.match import Match
from app.models.usuario import Usuario

def seed_predictions():
    db = SessionLocal()
    
    # 1. Asegurar que exista el usuario 1
    user = db.query(Usuario).filter(Usuario.id == 1).first()
    if not user:
        user = Usuario(id=1, username="Juancito", total_points=3)
        db.add(user)
        db.commit()

    # 2. Limpiar predicciones anteriores
    db.query(Prediction).delete()
    db.commit()

    # 3. Obtener los 3 partidos que insertamos antes
    # Ordenados por id para coincidir: Argentina, Brasil, España
    matches = db.query(Match).order_by(Match.id).limit(3).all()
    if len(matches) < 3:
        print("No se encontraron los 3 partidos. Por favor corre seed_matches.py primero.")
        db.close()
        return

    m1, m2, m3 = matches[0], matches[1], matches[2]

    # Predicción 1: Pleno Exacto (2 puntos - Borde Dorado)
    # Partido: Argentina vs Polonia
    p1 = Prediction(
        user_id=1, 
        match_id=m1.id, 
        score_home_predicted=2, 
        score_away_predicted=0, 
        points_earned=2
    )

    # Predicción 2: Solo tendencia ganadora (1 punto - Borde Blanco)
    # Partido: Brasil vs Suiza (Va ganando Brasil 1-0)
    p2 = Prediction(
        user_id=1, 
        match_id=m2.id, 
        score_home_predicted=3, 
        score_away_predicted=0, 
        points_earned=1
    )

    # Predicción 3: Fallo total (0 puntos - Borde Rojo)
    # Partido: España vs Alemania (Terminó 1-1)
    p3 = Prediction(
        user_id=1, 
        match_id=m3.id, 
        score_home_predicted=2, 
        score_away_predicted=0, 
        points_earned=0
    )

    db.add_all([p1, p2, p3])
    db.commit()
    db.close()
    print("Predicciones de prueba agregadas exitosamente para ver los efectos de brillos.")

if __name__ == "__main__":
    seed_predictions()
