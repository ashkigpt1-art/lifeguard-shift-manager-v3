from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

import jdatetime
from sqlmodel import Session

from ..models.lifeguard import Lifeguard
from ..models.location import Location
from ..models.setting import Setting
from ..models.shift_history import ShiftHistory


@dataclass
class GuardState:
    guard: Lifeguard
    assignments: List[tuple[datetime, datetime]]
    breaks: List[tuple[datetime, datetime]]

    def is_available(self, start: datetime, end: datetime) -> bool:
        for b_start, b_end in self.breaks:
            if not (end <= b_start or start >= b_end):
                return False
        for a_start, a_end in self.assignments:
            if not (end <= a_start or start >= a_end):
                return False
        return True

    def assign(self, start: datetime, end: datetime) -> None:
        self.assignments.append((start, end))

    def block(self, start: datetime, end: datetime) -> None:
        self.breaks.append((start, end))


class AllocationContext:
    def __init__(self, session: Session):
        self.session = session
        self.setting: Setting = session.get(Setting, 1)
        if not self.setting:
            raise ValueError("Settings missing")
        self.today = datetime.now().date()
        self.start_dt = datetime.combine(self.today, datetime.strptime(self.setting.start, "%H:%M").time())
        self.end_dt = datetime.combine(self.today, datetime.strptime(self.setting.end, "%H:%M").time())
        self.history_rows: List[dict] = []
        self.wide_rows: List[dict] = []
        self.long_rows: List[dict] = []
        self.caption = ""
        self.generated_wide_header: List[str] = []
        self.generated_check_header: List[str] = []
        self.last_allocation_cache: Dict[str, List[dict]] = {}

    def jalali_today(self) -> str:
        today_j = jdatetime.datetime.fromgregorian(date=self.today)
        return today_j.strftime("%Y/%m/%d")


SKILL_TO_DIFFICULTY = {
    "expert": {"easy", "medium", "hard"},
    "medium": {"easy", "medium"},
    "low": {"easy"},
}

ROLE_PRIORITY = {
    "سر ناجی": 0,
    "ناجی": 1,
    "ناجی چک": 2,
}

CHECK_PRIORITY = {
    "ناجی چک": 0,
    "سر ناجی": 1,
    "ناجی": 2,
}


class AllocationEngine:
    def __init__(self, session: Session):
        self.ctx = AllocationContext(session)
        self.session = session
        self.setting = self.ctx.setting
        self.lifeguards = self._load_lifeguards()
        self.locations = self._load_locations()
        self.jalali_date = self.ctx.jalali_today()
        self.long_cache: List[dict] = []
        self.wide_cache: List[dict] = []

    def _load_lifeguards(self) -> Dict[str, GuardState]:
        guards = {
            g.name: GuardState(guard=g, assignments=[], breaks=[])
            for g in self.session.query(Lifeguard).filter(Lifeguard.present == True).all()  # noqa: E712
        }
        lunch_window = timedelta(minutes=self.setting.lunch_min + self.setting.shower_min)
        dinner_window = timedelta(minutes=self.setting.dinner_min)
        dinner_start = datetime.combine(self.ctx.today, datetime.strptime("17:00", "%H:%M").time())
        for guard_state in guards.values():
            guard = guard_state.guard
            if guard.lunch_at and guard.lunch_at != "-":
                start = datetime.combine(self.ctx.today, datetime.strptime(guard.lunch_at, "%H:%M").time())
                guard_state.block(start, start + lunch_window)
            if guard.swap_at and guard.swap_at != "-" and guard.backup_name and guard.backup_name != "-":
                swap_time = datetime.combine(self.ctx.today, datetime.strptime(guard.swap_at, "%H:%M").time())
                guard_state.block(swap_time, swap_time)
            guard_state.block(dinner_start, dinner_start + dinner_window)
        return guards

    def _load_locations(self) -> List[Location]:
        return (
            self.session.query(Location)
            .filter(Location.active_today == True)  # noqa: E712
            .order_by(Location.difficulty.desc())
            .all()
        )

    def _slot_length(self, location: Location) -> timedelta:
        hours = self.setting.special_hours if ("(" in location.name or "چاله" in location.name) else self.setting.shift_hours
        return timedelta(hours=hours)

    def _build_slots(self, location: Location) -> List[tuple[datetime, datetime]]:
        slots = []
        slot_length = self._slot_length(location)
        start = self.ctx.start_dt
        index = 0
        while start < self.ctx.end_dt:
            end = min(start + slot_length, self.ctx.end_dt)
            slots.append((start, end))
            start = end
            index += 1
        return slots

    def _score_guard(self, guard_state: GuardState, location: Location, slot_start: datetime, slot_end: datetime) -> tuple:
        guard = guard_state.guard
        difficulty_match = location.difficulty in SKILL_TO_DIFFICULTY.get(guard.experience, {"easy"})
        if not difficulty_match:
            return (99, 99, 99, guard.name)
        role_priority = ROLE_PRIORITY.get(guard.role, 3)
        is_water = location.is_water
        if guard.role == "ناجی چک" and is_water:
            role_priority += 1
        if guard.role == "سر ناجی" and location.difficulty == "hard":
            role_priority -= 1
        repeat_penalty = 0
        if self.session.query(ShiftHistory).filter(
            ShiftHistory.date_jalali == self.jalali_date,
            ShiftHistory.guard_name == guard.name,
            ShiftHistory.location_name == location.name,
        ).count() > 0:
            repeat_penalty = 5
        return (role_priority + repeat_penalty, len(guard_state.assignments), guard_state.guard.name)

    def _check_lunch_concurrency(self, start: datetime, end: datetime, guard_state: GuardState) -> bool:
        if guard_state.guard.lunch_at in (None, "-"):
            return True
        lunch_time = datetime.combine(self.ctx.today, datetime.strptime(guard_state.guard.lunch_at, "%H:%M").time())
        lunch_end = lunch_time + timedelta(minutes=self.setting.lunch_min + self.setting.shower_min)
        if end <= lunch_time or start >= lunch_end:
            return True
        overlapping = 0
        for other_state in self.lifeguards.values():
            if other_state.guard.name == guard_state.guard.name:
                continue
            if other_state.guard.lunch_at in (None, "-"):
                continue
            other_start = datetime.combine(self.ctx.today, datetime.strptime(other_state.guard.lunch_at, "%H:%M").time())
            other_end = other_start + timedelta(minutes=self.setting.lunch_min + self.setting.shower_min)
            if not (lunch_end <= other_start or lunch_time >= other_end):
                overlapping += 1
        return overlapping < self.setting.max_concurrent_lunch

    def allocate(self) -> dict:
        long_rows: List[dict] = []
        wide_rows: List[dict] = []
        history_rows: List[dict] = []
        wide_headers: Dict[str, int] = defaultdict(int)
        check_rot = deque([name for name, g in self.lifeguards.items() if g.guard.role == "ناجی چک"])
        if not check_rot:
            fallback = [name for name, g in self.lifeguards.items() if g.guard.role == "سر ناجی"]
            if not fallback:
                fallback = [name for name in self.lifeguards.keys()]
            check_rot = deque(fallback)

        for location in self.locations:
            slots = self._build_slots(location)
            row = {"لوکیشن": location.name}
            for idx, (slot_start, slot_end) in enumerate(slots, start=1):
                candidate = self._select_guard(location, slot_start, slot_end)
                if not candidate:
                    cell_value = "--"
                else:
                    guard_state = self.lifeguards[candidate]
                    guard_state.assign(slot_start, slot_end)
                    cell_value, entries = self._build_assignment(guard_state, location, slot_start, slot_end)
                    history_rows.extend(entries)
                    long_rows.extend(entries)
                header = f"شیفت {idx} ({slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')})"
                row[header] = cell_value
                wide_headers[header] += 1
            wide_rows.append(row)

            if location.is_water:
                for idx, minute in enumerate(self.setting.check_windows, start=1):
                    check_start = self.ctx.start_dt + timedelta(minutes=minute)
                    check_end = min(check_start + timedelta(minutes=self.setting.check_window_len_min), self.ctx.end_dt)
                    assignee_name = self._rotate_check(check_rot)
                    check_state = self.lifeguards.get(assignee_name)
                    if check_state and check_state.is_available(check_start, check_end):
                        check_state.assign(check_start, check_end)
                        entry = {
                            "Location": location.name,
                            "Start": check_start.strftime("%H:%M"),
                            "End": check_end.strftime("%H:%M"),
                            "Assignee": assignee_name,
                            "Kind": "Check",
                        }
                        long_rows.append(entry)
                        history_rows.append({
                            "guard_name": assignee_name,
                            "location_name": f"چک - {location.name}",
                            "start": entry["Start"],
                            "end": entry["End"],
                            "kind": "Check",
                        })
                        row[f"چک {idx}"] = assignee_name
                    else:
                        row[f"چک {idx}"] = "--"

        caption = (
            f"تاریخ: {self.jalali_date} | از {self.setting.start} تا {self.setting.end} — برنامه تولید شد ✅"
        )
        self.long_cache = long_rows
        self.wide_cache = wide_rows
        self.ctx.caption = caption
        self._persist_history(history_rows)
        return {
            "wide": wide_rows,
            "long": long_rows,
            "team": [self._guard_to_dict(g.guard) for g in self.lifeguards.values()],
            "history": history_rows,
            "caption": caption,
        }

    def _rotate_check(self, queue: deque[str]) -> str:
        queue.rotate(-1)
        return queue[0]

    def _guard_to_dict(self, guard: Lifeguard) -> dict:
        return {
            "id": guard.id,
            "name": guard.name,
            "experience": guard.experience,
            "role": guard.role,
            "team": guard.team,
        }

    def _build_assignment(
        self, guard_state: GuardState, location: Location, slot_start: datetime, slot_end: datetime
    ) -> tuple[str, List[dict]]:
        guard = guard_state.guard
        swap_at = guard.swap_at if guard.swap_at and guard.swap_at != "-" else None
        entries: List[dict] = []
        if swap_at and guard.backup_name and guard.backup_name != "-":
            swap_time = datetime.combine(self.ctx.today, datetime.strptime(swap_at, "%H:%M").time())
            if slot_start < swap_time < slot_end:
                backup_state = self.lifeguards.get(guard.backup_name)
                if backup_state and backup_state.is_available(swap_time, slot_end):
                    backup_state.assign(swap_time, slot_end)
                    entries.append(
                        {
                            "Location": location.name,
                            "Start": slot_start.strftime("%H:%M"),
                            "End": swap_time.strftime("%H:%M"),
                            "Assignee": guard.name,
                            "Kind": "General" if not location.is_water else "Water",
                        }
                    )
                    entries.append(
                        {
                            "Location": location.name,
                            "Start": swap_time.strftime("%H:%M"),
                            "End": slot_end.strftime("%H:%M"),
                            "Assignee": backup_state.guard.name,
                            "Kind": "General" if not location.is_water else "Water",
                        }
                    )
                    text = f"{guard.name} ({slot_start.strftime('%H:%M')}-{swap_time.strftime('%H:%M')}) | {backup_state.guard.name} ({swap_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')})"
                    return text, entries
        entries.append(
            {
                "Location": location.name,
                "Start": slot_start.strftime("%H:%M"),
                "End": slot_end.strftime("%H:%M"),
                "Assignee": guard.name,
                "Kind": "Water" if location.is_water else "General",
            }
        )
        text = f"{guard.name}"
        return text, entries

    def _select_guard(self, location: Location, slot_start: datetime, slot_end: datetime) -> Optional[str]:
        candidates = []
        for name, state in self.lifeguards.items():
            if not state.is_available(slot_start, slot_end):
                continue
            if not self._check_lunch_concurrency(slot_start, slot_end, state):
                continue
            if location.is_water and state.guard.role == "ناجی چک":
                continue
            if state.guard.role == "سر ناجی" and location.is_water and location.difficulty != "hard":
                continue
            score = self._score_guard(state, location, slot_start, slot_end)
            if score[0] < 99:
                candidates.append((score, name))
        if not candidates:
            for name, state in self.lifeguards.items():
                if not state.is_available(slot_start, slot_end):
                    continue
                score = self._score_guard(state, location, slot_start, slot_end)
                candidates.append((score, name))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def _persist_history(self, entries: List[dict]) -> None:
        existing = self.session.query(ShiftHistory).filter(ShiftHistory.date_jalali == self.jalali_date)
        existing.delete()
        for entry in entries:
            self.session.add(
                ShiftHistory(
                    date_jalali=self.jalali_date,
                    guard_name=entry.get("guard_name") or entry.get("Assignee"),
                    location_name=entry.get("location_name") or entry.get("Location"),
                    start=entry.get("start") or entry.get("Start"),
                    end=entry.get("end") or entry.get("End"),
                    kind=entry.get("kind") or entry.get("Kind", "General"),
                )
            )
        self.session.commit()

    def export_wide_csv(self) -> bytes:
        import csv
        import io

        if not self.wide_cache:
            raise ValueError("No allocation available")
        headers = list(self.wide_cache[0].keys())
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=headers)
        writer.writeheader()
        for row in self.wide_cache:
            writer.writerow(row)
        return buffer.getvalue().encode("utf-8")

    def export_long_csv(self) -> bytes:
        import csv
        import io

        if not self.long_cache:
            raise ValueError("No allocation available")
        headers = list(self.long_cache[0].keys())
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=headers)
        writer.writeheader()
        for row in self.long_cache:
            writer.writerow(row)
        return buffer.getvalue().encode("utf-8")
