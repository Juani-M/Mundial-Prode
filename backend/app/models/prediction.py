from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    score_home_predicted = Column(Integer, nullable=False)
    score_away_predicted = Column(Integer, nullable=False)
    points_earned = Column(Integer, nullable=True)
