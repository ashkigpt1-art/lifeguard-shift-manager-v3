from collections.abc import Generator
from sqlmodel import Session

from .config import get_settings
from ..db import engine


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_cors_origins() -> list[str]:
    return get_settings().cors_origins
