from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Partido(Base):
    """
    Partido del Mundial.
    estado: 'pendiente' | 'en_curso' | 'finalizado'
    fase:   'Grupos' | '16avos' | 'Octavos' | 'Cuartos' | 'Semifinal' | 'Final'
    """
    __tablename__ = "partidos"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Equipos (FK a la tabla equipos)
    equipo1_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    equipo2_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)

    # Resultado (None mientras no se jugó / está en curso)
    goles_equipo1 = Column(Integer, nullable=True)
    goles_equipo2 = Column(Integer, nullable=True)

    # Metadatos del partido
    estado = Column(String(20), default="pendiente", nullable=False)
    fase = Column(String(20), default="Grupos", nullable=False)
    fecha_hora = Column(DateTime, nullable=True)

    # Relaciones
    equipo1 = relationship("Equipo", foreign_keys=[equipo1_id])
    equipo2 = relationship("Equipo", foreign_keys=[equipo2_id])
    predicciones = relationship("Prediccion", back_populates="partido")
