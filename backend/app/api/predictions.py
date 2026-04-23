from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.prediction import Prediction
from app.models.usuario import Usuario
from app.models.match import Match
from app.schemas.prediction import PredictionCreate, PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(pred_in: PredictionCreate, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == pred_in.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    match = db.query(Match).filter(Match.id == pred_in.match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partido no encontrado.")
    
    new_pred = Prediction(
        user_id=pred_in.user_id,
        match_id=pred_in.match_id,
        score_home_predicted=pred_in.score_home_predicted,
        score_away_predicted=pred_in.score_away_predicted
    )
    db.add(new_pred)
    db.commit()
    db.refresh(new_pred)
    return new_pred

@router.get("/user/{user_id}", response_model=List[PredictionResponse])
def get_user_predictions(user_id: int, db: Session = Depends(get_db)):
    predictions = db.query(Prediction).filter(Prediction.user_id == user_id).all()
    return predictions
