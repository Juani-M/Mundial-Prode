from pydantic import BaseModel, ConfigDict
from typing import Optional

class PredictionCreate(BaseModel):
    user_id: int
    match_id: int
    score_home_predicted: int
    score_away_predicted: int

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    match_id: int
    score_home_predicted: int
    score_away_predicted: int
    points_earned: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
