from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.database import get_db
from app.core.config import settings
from app.models.usuario import Usuario

router = APIRouter()

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID


class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/google-login")
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        # Verify the token with Google (allowing 10 seconds of clock skew)
        idinfo = id_token.verify_oauth2_token(
            request.token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
        )

        email = idinfo.get("email")
        google_id = idinfo.get("sub")
        
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Token no válido (email o google_id faltante)")

        name = idinfo.get("name") or idinfo.get("given_name") or email.split("@")[0]

        # Check if user exists
        user = db.query(Usuario).filter(Usuario.google_id == google_id).first()
        
        if not user:
            # Check if user exists by email (if they registered differently)
            user = db.query(Usuario).filter(Usuario.email == email).first()
            if user:
                # Update existing user to link google account
                user.google_id = google_id
                db.commit()
                db.refresh(user)

        if not user:
            # Create new user
            user = Usuario(
                username=name,
                email=email,
                google_id=google_id,
                total_points=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return {
            "message": "Login exitoso",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "total_points": user.total_points
            }
        }

    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
