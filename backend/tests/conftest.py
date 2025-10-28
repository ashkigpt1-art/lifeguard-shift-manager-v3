from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.db import engine, init_db, session_scope
from app.services.import_export import seed_if_empty


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    with session_scope() as session:
        seed_if_empty(session)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def session():
    with Session(engine) as s:
        yield s
