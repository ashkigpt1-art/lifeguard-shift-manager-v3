from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ShiftHistoryRead(BaseModel):
    id: int
    date_jalali: str
    guard_name: str
    location_name: str
    start: str
    end: str
    kind: str
    created_at: datetime


class AllocationRequest(BaseModel):
    date: Optional[str] = None


class WideRow(BaseModel):
    data: dict[str, str]


class LongRow(BaseModel):
    Location: str
    Start: str
    End: str
    Assignee: str
    Kind: str


class AllocationResponse(BaseModel):
    wide: List[dict]
    long: List[dict]
    team: List[dict]
    history: List[dict]
    caption: str
