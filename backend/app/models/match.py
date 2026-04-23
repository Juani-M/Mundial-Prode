from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_home = Column(String(50), nullable=False)
    team_away = Column(String(50), nullable=False)
    match_date = Column(DateTime, nullable=False)
    phase = Column(String(50), nullable=False)
    
    score_home_actual = Column(Integer, nullable=True)
    score_away_actual = Column(Integer, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
