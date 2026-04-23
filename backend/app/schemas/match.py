from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MatchCreate(BaseModel):
    team_home: str
    team_away: str
    match_date: datetime
    phase: str

class MatchResolve(BaseModel):
    score_home_actual: int
    score_away_actual: int

class MatchResponse(BaseModel):
    id: int
    team_home: str
    team_away: str
    match_date: datetime
    phase: str
    score_home_actual: Optional[int] = None
    score_away_actual: Optional[int] = None
    status: str

    model_config = ConfigDict(from_attributes=True)
