"""Shared dates and places for the journey, independent of Streamlit."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import NamedTuple
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Europe/Budapest")
FIRST_MEMORY = datetime(2025, 1, 4, tzinfo=TIMEZONE)
NEXT_MEETING = datetime(2026, 11, 12, tzinfo=TIMEZONE)

CITIES = {
    "Praga": {
        "label": "Praga",
        "country": "Chequia",
        "country_geojson": "Czechia",
        "lat": 50.0755,
        "lon": 14.4378,
        "description": "Entre puentes, calles y recuerdos.",
    },
    "Paris": {
        "label": "París",
        "country": "Francia",
        "country_geojson": "France",
        "lat": 48.8566,
        "lon": 2.3522,
        "description": "Una ciudad que también vive en nuestras fotos.",
    },
    "Monterrey": {
        "label": "Monterrey",
        "country": "México",
        "country_geojson": "Mexico",
        "lat": 25.6866,
        "lon": -100.3161,
        "description": "Paisajes que se vuelven parte de la historia.",
    },
}


@dataclass(frozen=True)
class Milestone:
    date: datetime
    label: str
    city: str | None = None


MILESTONES = (
    Milestone(FIRST_MEMORY, "Primer beso"),
    Milestone(datetime(2025, 5, 10, tzinfo=TIMEZONE), "Praga", "Praga"),
    Milestone(datetime(2025, 6, 6, tzinfo=TIMEZONE), "Monterrey", "Monterrey"),
    Milestone(datetime(2025, 11, 14, tzinfo=TIMEZONE), "Monterrey", "Monterrey"),
    Milestone(datetime(2026, 9, 12, tzinfo=TIMEZONE), "Reencuentro"),
    Milestone(NEXT_MEETING, "Eurotrip"),
)


class CountdownParts(NamedTuple):
    days: int
    hours: int
    minutes: int
    seconds: int


def _instant(value: datetime) -> datetime:
    """Interpret naive dates in Budapest and compare all dates in UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        value = value.replace(tzinfo=TIMEZONE)
    return value.astimezone(timezone.utc)


def countdown_parts(now: datetime | None = None) -> CountdownParts:
    """Return whole remaining seconds, clamped at zero after departure.

    A naive ``now`` means local Budapest time, regardless of the host timezone.
    Aware dates retain their instant, including across daylight saving changes.
    """
    current = now if now is not None else datetime.now(TIMEZONE)
    remaining = max(0, int((_instant(NEXT_MEETING) - _instant(current)).total_seconds()))
    days, remainder = divmod(remaining, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return CountdownParts(days, hours, minutes, seconds)


def timeline_progress(now: datetime | None = None) -> float:
    """Elapsed fraction from the first memory to Eurotrip, between zero and one."""
    current = now if now is not None else datetime.now(TIMEZONE)
    start = _instant(FIRST_MEMORY)
    duration = (_instant(NEXT_MEETING) - start).total_seconds()
    elapsed = (_instant(current) - start).total_seconds()
    return max(0.0, min(1.0, elapsed / duration))


def route_position(now: datetime | None = None) -> float:
    """Place the plane between evenly spaced stops according to their dates."""
    progress = timeline_progress(now)
    stops = [timeline_progress(milestone.date) for milestone in MILESTONES]
    for index in range(len(stops) - 1):
        if progress <= stops[index + 1]:
            fraction = (progress - stops[index]) / (stops[index + 1] - stops[index])
            return (index + fraction) / (len(stops) - 1)
    return 1.0


def formatted_coordinates(city_key: str) -> str:
    """Show a city's latitude and longitude with geographic hemispheres."""
    city = CITIES[city_key]
    lat, lon = city["lat"], city["lon"]
    return (
        f"{abs(lat):.4f}° {'N' if lat >= 0 else 'S'} · "
        f"{abs(lon):.4f}° {'E' if lon >= 0 else 'O'}"
    )
