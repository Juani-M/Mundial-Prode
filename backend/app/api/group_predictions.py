from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.group_prediction import GroupPrediction
from app.models.group_result import GroupResult
from app.models.usuario import Usuario
from app.schemas.group_prediction import GroupPredictionCreate, GroupPredictionResponse, GroupResultCreate

router = APIRouter(prefix="/group-predictions", tags=["group_predictions"])

@router.get("/user/{user_id}", response_model=List[GroupPredictionResponse])
def get_user_group_predictions(user_id: int, db: Session = Depends(get_db)):
    predictions = db.query(GroupPrediction).filter(GroupPrediction.user_id == user_id).all()
    return predictions

@router.post("/", response_model=GroupPredictionResponse)
def create_or_update_group_prediction(pred_in: GroupPredictionCreate, db: Session = Depends(get_db)):
    # Check if prediction already exists for this user and group
    db_pred = db.query(GroupPrediction).filter(
        GroupPrediction.user_id == pred_in.user_id,
        GroupPrediction.group_name == pred_in.group_name
    ).first()

    if db_pred:
        # Update
        db_pred.pos1_team = pred_in.pos1_team
        db_pred.pos2_team = pred_in.pos2_team
        db_pred.pos3_team = pred_in.pos3_team
        db_pred.pos4_team = pred_in.pos4_team
        db.commit()
        db.refresh(db_pred)
        return db_pred
    else:
        # Create
        new_pred = GroupPrediction(
            user_id=pred_in.user_id,
            group_name=pred_in.group_name,
            pos1_team=pred_in.pos1_team,
            pos2_team=pred_in.pos2_team,
            pos3_team=pred_in.pos3_team,
            pos4_team=pred_in.pos4_team
        )
        db.add(new_pred)
        db.commit()
        db.refresh(new_pred)
        return new_pred

@router.put("/{group_name}/resolve")
def resolve_group(group_name: str, result_in: GroupResultCreate, db: Session = Depends(get_db)):
    # 1. Update or create group result
    db_result = db.query(GroupResult).filter(GroupResult.group_name == group_name).first()
    if not db_result:
        db_result = GroupResult(
            group_name=group_name,
            pos1_team=result_in.pos1_team,
            pos2_team=result_in.pos2_team,
            pos3_team=result_in.pos3_team,
            pos4_team=result_in.pos4_team
        )
        db.add(db_result)
    else:
        db_result.pos1_team = result_in.pos1_team
        db_result.pos2_team = result_in.pos2_team
        db_result.pos3_team = result_in.pos3_team
        db_result.pos4_team = result_in.pos4_team

    # 2. Get all predictions for this group and calculate points
    predictions = db.query(GroupPrediction).filter(GroupPrediction.group_name == group_name).all()
    
    for pred in predictions:
        # Puntos anteriores para restar del usuario si se re-resuelve
        puntos_anteriores = pred.points_earned or 0
        
        # Calcular nuevos puntos
        aciertos = 0
        if pred.pos1_team == result_in.pos1_team: aciertos += 1
        if pred.pos2_team == result_in.pos2_team: aciertos += 1
        if pred.pos3_team == result_in.pos3_team: aciertos += 1
        if pred.pos4_team == result_in.pos4_team: aciertos += 1
        
        nuevos_puntos = aciertos
        
        pred.points_earned = nuevos_puntos
        
        # Update user total points
        user = db.query(Usuario).filter(Usuario.id == pred.user_id).first()
        if user:
            user.total_points = user.total_points - puntos_anteriores + nuevos_puntos
            
    db.commit()
    return {"message": f"Grupo {group_name} resuelto correctamente."}
