from typing import Optional

from sqlmodel import Field, SQLModel


class Location(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    difficulty: str = Field(default="medium")
    is_water: bool = Field(default=False)
    active_today: bool = Field(default=True)
