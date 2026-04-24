from sqlalchemy import Column, String
from app.core.database import Base

class GroupResult(Base):
    __tablename__ = "group_results"

    group_name = Column(String(50), primary_key=True, index=True)
    pos1_team = Column(String(50), nullable=False)
    pos2_team = Column(String(50), nullable=False)
    pos3_team = Column(String(50), nullable=False)
    pos4_team = Column(String(50), nullable=False)
