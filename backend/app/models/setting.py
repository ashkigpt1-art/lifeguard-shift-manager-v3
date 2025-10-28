from sqlmodel import Field, SQLModel


class Setting(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    start: str = Field(default="09:00")
    end: str = Field(default="22:00")
    shift_hours: float = Field(default=2.0)
    special_hours: float = Field(default=1.5)
    lunch_min: int = Field(default=20)
    dinner_min: int = Field(default=10)
    shower_min: int = Field(default=10)
    max_concurrent_lunch: int = Field(default=2)
    check_windows_min: str = Field(default="30,60,90,120")
    check_window_len_min: int = Field(default=10)

    @property
    def check_windows(self) -> list[int]:
        return [int(v) for v in self.check_windows_min.split(",") if v]
