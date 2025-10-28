from typing import List

from pydantic import BaseModel


class SettingRead(BaseModel):
    start: str
    end: str
    shift_hours: float
    special_hours: float
    lunch_min: int
    dinner_min: int
    shower_min: int
    max_concurrent_lunch: int
    check_windows_min: List[int]
    check_window_len_min: int


class SettingUpdate(SettingRead):
    pass
