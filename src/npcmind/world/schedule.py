"""DailySchedule - NPC routine and activity planning."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ScheduleEntry(BaseModel):
    """A single block of time in an NPC's daily routine."""

    hour_start: int = Field(ge=0, le=23)
    hour_end: int = Field(ge=0, le=23)
    activity: str
    location: str
    priority: int = Field(1, ge=1, le=10, description="Higher = harder to interrupt")
    interruptible: bool = True
    notes: str = ""


class DailySchedule:
    """Manages an NPC's repeating daily routine."""

    def __init__(self, entries: Optional[list[ScheduleEntry]] = None) -> None:
        self.entries: list[ScheduleEntry] = entries or []

    def add(self, entry: ScheduleEntry) -> None:
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.hour_start)

    def remove_at(self, hour: int) -> bool:
        before = len(self.entries)
        self.entries = [e for e in self.entries if not (e.hour_start <= hour < e.hour_end)]
        return len(self.entries) < before

    def current_activity(self, hour: int) -> Optional[ScheduleEntry]:
        """Return the schedule entry active at the given hour (0-23)."""
        for entry in self.entries:
            if entry.hour_start <= hour < entry.hour_end:
                return entry
            # Handle wrap-around (e.g., 22 to 6)
            if entry.hour_start > entry.hour_end:
                if hour >= entry.hour_start or hour < entry.hour_end:
                    return entry
        return None

    def location_at(self, hour: int) -> str:
        entry = self.current_activity(hour)
        return entry.location if entry else "unknown"

    def is_busy(self, hour: int) -> bool:
        entry = self.current_activity(hour)
        return entry is not None and not entry.interruptible

    def to_list(self) -> list[dict]:
        return [e.model_dump() for e in self.entries]

    @classmethod
    def merchant_default(cls) -> DailySchedule:
        """Standard merchant daily routine."""
        return cls(entries=[
            ScheduleEntry(hour_start=6, hour_end=7, activity="breakfast", location="home", priority=2),
            ScheduleEntry(hour_start=7, hour_end=8, activity="open shop", location="market", priority=3),
            ScheduleEntry(hour_start=8, hour_end=12, activity="trading", location="market", priority=5, interruptible=True),
            ScheduleEntry(hour_start=12, hour_end=13, activity="lunch", location="tavern", priority=2),
            ScheduleEntry(hour_start=13, hour_end=18, activity="trading", location="market", priority=5, interruptible=True),
            ScheduleEntry(hour_start=18, hour_end=19, activity="close shop", location="market", priority=3),
            ScheduleEntry(hour_start=19, hour_end=21, activity="socializing", location="tavern", priority=1),
            ScheduleEntry(hour_start=21, hour_end=6, activity="sleeping", location="home", priority=8, interruptible=False),
        ])

    @classmethod
    def guard_default(cls) -> DailySchedule:
        """Standard guard daily routine."""
        return cls(entries=[
            ScheduleEntry(hour_start=6, hour_end=7, activity="breakfast", location="barracks", priority=2),
            ScheduleEntry(hour_start=7, hour_end=15, activity="patrol", location="streets", priority=7, interruptible=True),
            ScheduleEntry(hour_start=15, hour_end=16, activity="report", location="barracks", priority=5, interruptible=False),
            ScheduleEntry(hour_start=16, hour_end=18, activity="training", location="training_yard", priority=4),
            ScheduleEntry(hour_start=18, hour_end=20, activity="dinner and rest", location="barracks", priority=2),
            ScheduleEntry(hour_start=20, hour_end=6, activity="sleeping", location="barracks", priority=8, interruptible=False),
        ])
