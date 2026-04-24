from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class GroupPrediction(Base):
    __tablename__ = "group_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    group_name = Column(String(50), nullable=False)
    
    pos1_team = Column(String(50), nullable=False)
    pos2_team = Column(String(50), nullable=False)
    pos3_team = Column(String(50), nullable=False)
    pos4_team = Column(String(50), nullable=False)
    
    points_earned = Column(Integer, nullable=True)
