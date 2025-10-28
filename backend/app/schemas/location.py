from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    is_water: bool = False
    active_today: bool = True


class LocationCreate(LocationBase):
    pass


class LocationRead(LocationBase):
    id: int


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    is_water: Optional[bool] = None
    active_today: Optional[bool] = None
