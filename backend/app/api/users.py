from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el username ya existe
    user_db = db.query(Usuario).filter(Usuario.username == user_in.username).first()
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado."
        )
    
    # Crear nuevo usuario
    new_user = Usuario(
        username=user_in.username,
        total_points=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/ranking", response_model=List[UserResponse])
def get_ranking(db: Session = Depends(get_db)):
    # Traer a los usuarios ordenados por puntos de mayor a menor
    users = db.query(Usuario).order_by(Usuario.total_points.desc()).all()
    return users
