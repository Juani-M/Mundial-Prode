from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Usuario(Base):
    """
    Participante del prode.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=False, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    google_id = Column(String(100), unique=True, index=True, nullable=True)
    total_points = Column(Integer, default=0, nullable=False)
