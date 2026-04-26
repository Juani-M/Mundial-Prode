from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.prediction import Prediction
from app.models.usuario import Usuario
from app.models.match import Match
from app.schemas.prediction import PredictionCreate, PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def create_or_update_prediction(pred_in: PredictionCreate, db: Session = Depends(get_db)):
    # Verificar que el usuario exista
    user = db.query(Usuario).filter(Usuario.id == pred_in.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

    # Verificar que el partido exista
    match = db.query(Match).filter(Match.id == pred_in.match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partido no encontrado.")

    # ❌ No se puede predecir un partido que ya empezó o terminó
    if match.status in ("finished", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede predecir un partido que ya comenzó o finalizó.",
        )

    # Upsert: buscar predicción existente del mismo usuario para el mismo partido
    existing = db.query(Prediction).filter(
        Prediction.user_id == pred_in.user_id,
        Prediction.match_id == pred_in.match_id,
    ).first()

    if existing:
        # Actualizar predicción existente
        existing.score_home_predicted = pred_in.score_home_predicted
        existing.score_away_predicted = pred_in.score_away_predicted
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Crear nueva predicción
        new_pred = Prediction(
            user_id=pred_in.user_id,
            match_id=pred_in.match_id,
            score_home_predicted=pred_in.score_home_predicted,
            score_away_predicted=pred_in.score_away_predicted,
        )
        db.add(new_pred)
        db.commit()
        db.refresh(new_pred)
        return new_pred


@router.get("/user/{user_id}", response_model=List[PredictionResponse])
def get_user_predictions(user_id: int, db: Session = Depends(get_db)):
    predictions = db.query(Prediction).filter(Prediction.user_id == user_id).all()
    return predictions
