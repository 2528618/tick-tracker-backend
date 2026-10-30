from collections import Counter
from datetime import datetime

FIELDS = ["id", "date", "location", "species", "latinName"]


def check_data(sightings: list[dict]) -> dict:
    missing = {field: 0 for field in FIELDS}
    for record in sightings:
        for field in FIELDS:
            value = record.get(field)
            if value is None or str(value).strip() == "":
                missing[field] += 1

    id_counts = Counter(r.get("id") for r in sightings)
    duplicate_ids = {i: n for i, n in id_counts.items() if n > 1}

    keys = Counter(
        (r.get("date"), str(r.get("location")).strip().lower(), str(r.get("species")).strip().lower())
        for r in sightings
    )
    duplicate_sightings = sum(n - 1 for n in keys.values() if n > 1)

    bad_dates = []
    good_dates = []
    for r in sightings:
        try:
            good_dates.append(datetime.fromisoformat(str(r.get("date"))))
        except ValueError:
            bad_dates.append(r.get("date"))

    locations = Counter(r.get("location") for r in sightings)
    species = Counter(r.get("species") for r in sightings)
    species_latin_pairs = Counter((r.get("species"), r.get("latinName")) for r in sightings)

    return {
        "total_records": len(sightings),
        "missing_fields": missing,
        "duplicate_ids": duplicate_ids,
        "duplicate_sightings_same_data_place_species": duplicate_sightings,
        "unreable_dates": len(bad_dates),
        "earliest_date": min(good_dates) if good_dates else None,
        "latest_date": max(good_dates) if good_dates else None,
        "locations": dict(locations.most_common()),
        "species": dict(species.most_common()),
        "species_latin_pairs": [f"{s} = {l} ({n})" for (s, l), n in species_latin_pairs.most_common()],
    }

