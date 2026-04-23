from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Equipo(Base):
    """
    Selecciones participantes del Mundial.
    grupo: 'A' a 'H' en fase de grupos, None en fases eliminatorias.
    """
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)   # ej: "Argentina"
    codigo = Column(String(3), nullable=False, unique=True)     # ej: "ARG"
    grupo = Column(String(1), nullable=True)                    # ej: "A" … "H"
