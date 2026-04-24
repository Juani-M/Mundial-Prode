from pydantic import BaseModel
from typing import Optional

class GroupPredictionBase(BaseModel):
    group_name: str
    pos1_team: str
    pos2_team: str
    pos3_team: str
    pos4_team: str

class GroupPredictionCreate(GroupPredictionBase):
    user_id: int

class GroupPredictionResponse(GroupPredictionBase):
    id: int
    user_id: int
    points_earned: Optional[int] = None

    class Config:
        from_attributes = True

class GroupResultCreate(BaseModel):
    pos1_team: str
    pos2_team: str
    pos3_team: str
    pos4_team: str
