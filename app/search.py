"""Filtering and paging for sightings."""
from datetime import date


def search_sightings(
    sightings: list[dict],
    start_date: date | None = None,
    end_date: date | None = None,
    location: str | None = None,
    region: str | None = None,
    species: str | None = None,
) -> list[dict]:
    """Return only the sightings that match every filter given.

    Any filter left as None is ignored.
    """
    results = []
    for s in sightings:
        sighting_day = s["date"].date()  # just the day, without the time

        if start_date and sighting_day < start_date:
            continue
        if end_date and sighting_day > end_date:
            continue
        if location and s["location"].lower() != location.strip().lower():
            continue
        if region and s["region"].lower() != region.strip().lower():
            continue
        if species and s["species"].lower() != species.strip().lower():
            continue

        results.append(s)

    results.sort(key=lambda s: s["date"], reverse=True)  # newest first
    return results


def paginate(items: list, page: int, page_size: int) -> dict:
    """Return one 'page' of results."""
    start = (page - 1) * page_size
    total = len(items)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": items[start:start + page_size],
    }