from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re


DURATION_PATTERN = re.compile(r"(?P<value>\d+)\s*(?P<unit>[smhdw])", re.IGNORECASE)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_duration(duration: str) -> timedelta | None:
    text = duration.strip().lower()
    if not text:
        return None

    total = timedelta()
    position = 0
    for match in DURATION_PATTERN.finditer(text):
        if match.start() != position:
            return None
        value = int(match.group("value"))
        unit = match.group("unit")
        if unit == "s":
            total += timedelta(seconds=value)
        elif unit == "m":
            total += timedelta(minutes=value)
        elif unit == "h":
            total += timedelta(hours=value)
        elif unit == "d":
            total += timedelta(days=value)
        elif unit == "w":
            total += timedelta(weeks=value)
        position = match.end()

    if position != len(text) or total.total_seconds() <= 0:
        return None
    return total


def format_timedelta(value: timedelta | None) -> str:
    if value is None:
        return "Permanent"

    seconds = int(value.total_seconds())
    if seconds <= 0:
        return "0s"

    chunks: list[str] = []
    for suffix, unit_seconds in (("w", 604800), ("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        amount, seconds = divmod(seconds, unit_seconds)
        if amount:
            chunks.append(f"{amount}{suffix}")
    return " ".join(chunks)


def to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def from_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value).astimezone(timezone.utc)
