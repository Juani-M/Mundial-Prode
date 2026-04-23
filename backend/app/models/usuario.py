from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Usuario(Base):
    """
    Participante del prode.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    total_points = Column(Integer, default=0, nullable=False)
