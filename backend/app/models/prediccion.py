from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Prediccion(Base):
    """
    Pronóstico de un usuario para un partido.
    puntos_ganados se calcula y asigna cuando el partido finaliza.
    """
    __tablename__ = "predicciones"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relaciones
    usuario_legajo = Column(Integer, ForeignKey("usuarios.legajo"), nullable=False)
    partido_id = Column(Integer, ForeignKey("partidos.id"), nullable=False)

    # Pronóstico del usuario
    goles_local = Column(Integer, nullable=False)
    goles_visitante = Column(Integer, nullable=False)

    # Puntos asignados al corregir (None = aún no corregido)
    puntos_ganados = Column(Integer, nullable=True)

    # Relaciones ORM
    usuario = relationship("Usuario", foreign_keys=[usuario_legajo])
    partido = relationship("Partido", back_populates="predicciones")
