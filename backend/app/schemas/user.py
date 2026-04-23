from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    total_points: int

    model_config = ConfigDict(from_attributes=True)
