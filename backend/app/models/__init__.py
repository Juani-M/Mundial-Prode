# Importar todos los modelos para que SQLAlchemy los registre en Base.metadata
# y Alembic los detecte automáticamente en futuras migraciones.

from app.models.usuario import Usuario       # noqa: F401
from app.models.equipo import Equipo         # noqa: F401
from app.models.match import Match           # noqa: F401
from app.models.prediction import Prediction # noqa: F401
from app.models.group_prediction import GroupPrediction # noqa: F401
from app.models.group_result import GroupResult # noqa: F401
