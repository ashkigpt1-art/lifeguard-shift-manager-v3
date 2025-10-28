from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Iterable, List

import yaml
from fastapi import UploadFile
from sqlmodel import Session, select

from ..db import DATA_DIR
from ..models.lifeguard import Lifeguard
from ..models.location import Location
from ..models.setting import Setting


def seed_if_empty(session: Session) -> None:
    if session.exec(select(Lifeguard)).first() is None:
        load_lifeguards_from_csv(DATA_DIR / "lifeguards.csv", session)
    if session.exec(select(Location)).first() is None:
        load_locations_from_csv(DATA_DIR / "locations.csv", session)
    if session.get(Setting, 1) is None:
        load_settings_from_yaml(DATA_DIR / "settings.yaml", session)


def _read_csv(path: Path | UploadFile) -> Iterable[dict[str, str]]:
    if isinstance(path, UploadFile):
        data = path.file.read().decode("utf-8")
        path.file.seek(0)
    else:
        data = Path(path).read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(data))
    return list(reader)


def load_lifeguards_from_csv(path: Path | UploadFile, session: Session) -> None:
    rows = _read_csv(path)
    session.query(Lifeguard).delete()
    session.commit()
    records: List[Lifeguard] = []
    for row in rows:
        records.append(
            Lifeguard(
                name=row.get("name"),
                experience=row.get("experience", "medium"),
                present=str(row.get("present", "TRUE")).upper() == "TRUE",
                role=row.get("role", "ناجی") or "ناجی",
                lunch_at=row.get("lunch_at", "-"),
                backup_name=row.get("backup_name", "-"),
                swap_at=row.get("swap_at", "-"),
                team=row.get("team"),
            )
        )
    session.add_all(records)
    session.commit()


def export_lifeguards_to_csv(session: Session) -> bytes:
    guards = session.exec(select(Lifeguard)).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "name", "experience", "present", "role", "lunch_at", "backup_name", "swap_at", "team"])
    for g in guards:
        writer.writerow([g.id, g.name, g.experience, g.present, g.role, g.lunch_at, g.backup_name, g.swap_at, g.team])
    return buffer.getvalue().encode("utf-8")


def load_locations_from_csv(path: Path | UploadFile, session: Session) -> None:
    rows = _read_csv(path)
    session.query(Location).delete()
    session.commit()
    records = [
        Location(
            name=row.get("name"),
            difficulty=row.get("difficulty", "medium"),
            is_water=str(row.get("is_water", "FALSE")).upper() == "TRUE",
            active_today=str(row.get("active_today", "TRUE")).upper() == "TRUE",
        )
        for row in rows
    ]
    session.add_all(records)
    session.commit()


def export_locations_to_csv(session: Session) -> bytes:
    locations = session.exec(select(Location)).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "name", "difficulty", "is_water", "active_today"])
    for loc in locations:
        writer.writerow([loc.id, loc.name, loc.difficulty, loc.is_water, loc.active_today])
    return buffer.getvalue().encode("utf-8")


def load_settings_from_yaml(path: Path | UploadFile, session: Session) -> None:
    if isinstance(path, UploadFile):
        data = yaml.safe_load(path.file)
    else:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    payload = Setting(
        id=1,
        start=data.get("start", "09:00"),
        end=data.get("end", "22:00"),
        shift_hours=float(data.get("shift_hours", 2.0)),
        special_hours=float(data.get("special_hours", 1.5)),
        lunch_min=int(data.get("lunch_min", 20)),
        dinner_min=int(data.get("dinner_min", 10)),
        shower_min=int(data.get("shower_min", 10)),
        max_concurrent_lunch=int(data.get("max_concurrent_lunch", 2)),
        check_windows_min=",".join(str(x) for x in data.get("check_windows_min", [30, 60, 90, 120])),
        check_window_len_min=int(data.get("check_window_len_min", 10)),
    )
    session.merge(payload)
    session.commit()


def export_settings_to_yaml(session: Session) -> bytes:
    setting = session.get(Setting, 1)
    if not setting:
        raise ValueError("Settings not configured")
    payload = {
        "start": setting.start,
        "end": setting.end,
        "shift_hours": setting.shift_hours,
        "special_hours": setting.special_hours,
        "lunch_min": setting.lunch_min,
        "dinner_min": setting.dinner_min,
        "shower_min": setting.shower_min,
        "max_concurrent_lunch": setting.max_concurrent_lunch,
        "check_windows_min": setting.check_windows,
        "check_window_len_min": setting.check_window_len_min,
    }
    return yaml.safe_dump(payload, allow_unicode=True).encode("utf-8")
