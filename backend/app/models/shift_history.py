from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ShiftHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date_jalali: str
    guard_name: str
    location_name: str
    start: str
    end: str
    kind: str = Field(default="General")
    created_at: datetime = Field(default_factory=datetime.utcnow)
