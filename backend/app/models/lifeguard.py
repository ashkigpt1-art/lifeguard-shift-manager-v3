from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Lifeguard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    present: bool = Field(default=True)
    team: Optional[str] = None
    experience: str = Field(description="expert|medium|low")
    role: str = Field(default="ناجی")
    lunch_at: str = Field(default="-")
    backup_name: str = Field(default="-")
    swap_at: str = Field(default="-")
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
