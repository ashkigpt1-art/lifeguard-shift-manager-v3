from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LifeguardBase(BaseModel):
    name: str
    present: bool = True
    team: Optional[str] = None
    experience: str = Field(pattern="^(expert|medium|low)$")
    role: str = Field(default="ناجی")
    lunch_at: str = "-"
    backup_name: str = "-"
    swap_at: str = "-"


class LifeguardCreate(LifeguardBase):
    pass


class LifeguardRead(LifeguardBase):
    id: int
    updated_at: datetime


class LifeguardUpdate(BaseModel):
    name: Optional[str] = None
    present: Optional[bool] = None
    team: Optional[str] = None
    experience: Optional[str] = Field(default=None, pattern="^(expert|medium|low)$")
    role: Optional[str] = None
    lunch_at: Optional[str] = None
    backup_name: Optional[str] = None
    swap_at: Optional[str] = None
