from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.match import Match
from app.models.prediction import Prediction
from app.models.usuario import Usuario
from app.schemas.match import MatchCreate, MatchResponse, MatchResolve

router = APIRouter(prefix="/matches", tags=["matches"])

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(match_in: MatchCreate, db: Session = Depends(get_db)):
    new_match = Match(
        team_home=match_in.team_home,
        team_away=match_in.team_away,
        match_date=match_in.match_date,
        phase=match_in.phase,
        status="pending"
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match

@router.get("/", response_model=List[MatchResponse])
def get_matches(db: Session = Depends(get_db)):
    matches = db.query(Match).all()
    return matches

@router.put("/{match_id}/resolve")
def resolve_match(match_id: int, resolve_in: MatchResolve, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partido no encontrado.")
    
    if match.status == "finished":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El partido ya está finalizado.")

    # Actualizar resultado y estado
    match.score_home_actual = resolve_in.score_home_actual
    match.score_away_actual = resolve_in.score_away_actual
    match.status = "finished"

    # Traer todas las predicciones asociadas al partido
    predictions = db.query(Prediction).filter(Prediction.match_id == match_id).all()
    
    # Calcular tendencia del resultado real
    if match.score_home_actual > match.score_away_actual:
        actual_tendency = 1
    elif match.score_home_actual < match.score_away_actual:
        actual_tendency = -1
    else:
        actual_tendency = 0

    for pred in predictions:
        # Resultado exacto
        if pred.score_home_predicted == match.score_home_actual and pred.score_away_predicted == match.score_away_actual:
            pred.points_earned = 2
        else:
            # Tendencia
            if pred.score_home_predicted > pred.score_away_predicted:
                pred_tendency = 1
            elif pred.score_home_predicted < pred.score_away_predicted:
                pred_tendency = -1
            else:
                pred_tendency = 0
                
            if pred_tendency == actual_tendency:
                pred.points_earned = 1
            else:
                pred.points_earned = 0

        # Sumar puntos al usuario
        user = db.query(Usuario).filter(Usuario.id == pred.user_id).first()
        if user:
            user.total_points += pred.points_earned

    db.commit()
    return {"message": "Partido resuelto y puntos calculados exitosamente."}

