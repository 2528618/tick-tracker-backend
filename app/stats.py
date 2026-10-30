
from collections import Counter
from datetime import date, timedelta

def count_by(sightings: list[dict], field: str) -> list[dict]:
    """Count sightings by a given field (e.g., location, species)."""
    counts = Counter(s[field] for s in sightings)
    total = len(sightings)
    return [
        {"name": name, "count": n, "percent": round(100 * n / total, 1)}
        for name, n in counts.most_common()
    ]

def period_start(day: date, interval: str) -> date:
    if interval == "week":
        return day - timedelta(days=day.weekday())
    return day.replace(day=1)

def next_period(day: date, interval: str) -> date:
    if interval == "week":
        return day + timedelta(days=7)
    if day.month == 12:
        return date(day.year + 1, 1, 1)
    return date(day.year, day.month + 1, 1)

def trend(sightings : list[dict], interval: str) -> list[dict]:

    if not sightings:
        return []

    counts = Counter(period_start(s["date"].date(), interval) for s in sightings)

    points = []
    current = min(counts)
    last = max(counts)
    while current <= last:
        points.append({"period_start": current, "count": counts.get(current, 0)})
        current = next_period(current, interval)
    return points