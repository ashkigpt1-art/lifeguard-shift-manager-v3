from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlmodel import SQLModel, create_engine

from .core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})


@contextmanager
def session_scope() -> Iterator:
    from sqlmodel import Session

    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from .models import lifeguard, location, setting, shift_history  # noqa: F401

    SQLModel.metadata.create_all(engine)


DATA_DIR = Path(__file__).resolve().parent / "seeds"
