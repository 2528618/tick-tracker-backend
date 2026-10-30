
from datetime import datetime

CITIES = {
    "nottingham": ("Nottingham", "East Midlands", 52.9548, -1.1581),
    "leicester": ("Leicester", "East Midlands", 52.6369, -1.1398),
    "birmingham": ("Birmingham", "West Midlands", 52.4862, -1.8904),
    "london": ("London", "London", 51.5074, -0.1278),
    "southampton": ("Southampton", "South East", 50.9097, -1.4044),
    "bristol": ("Bristol", "South West", 51.4545, -2.5879),
    "manchester": ("Manchester", "North West", 53.4808, -2.2426),
    "liverpool": ("Liverpool", "North West", 53.4084, -2.9916),
    "leeds": ("Leeds", "Yorkshire and the Humber", 53.8008, -1.5491),
    "sheffield": ("Sheffield", "Yorkshire and the Humber", 53.3811, -1.4701),
    "newcastle": ("Newcastle", "North East", 54.9783, -1.6178),
    "glasgow": ("Glasgow", "Scotland", 55.8642, -4.2518),
    "edinburgh": ("Edinburgh", "Scotland", 55.9533, -3.1883),
    "cardiff": ("Cardiff", "Wales", 51.4816, -3.1791),
}

class InvalidRecord(Exception):
    """A record is too broken to use."""

def clean_record(raw: dict) -> dict:
    """Check and tidy one raw record from the Elanco API."""
    if not isinstance(raw, dict):
        raise InvalidRecord("Record is not a object")

    date_text = str(raw.get("date") or "").strip()
    if not date_text:
        raise InvalidRecord("Missing date") 
    try:
        date = datetime.fromisoformat(date_text)
    except ValueError:
        raise InvalidRecord(f"Invalid date: {date_text}")
    if date > datetime.now():
        raise InvalidRecord(f"Date is in the future: {date_text}")

    location_text = str(raw.get("location") or "").strip().lower()
    if not location_text:
        raise InvalidRecord("Missing location")
    city = CITIES.get(location_text)
    if city:
        location, region, lat, lon = city
    else:
        location, region, lat, lon = location_text.title(), "Unknown", None, None

    species = " ".join(str(raw.get("species") or "").split())
    if not species:
        raise InvalidRecord("Missing species")
    latin_name = " ".join(str(raw.get("latinName") or "").split()) or None

    return {
        "id": str(raw.get("id") or "").strip(),
        "date": date,
        "location": location,
        "region": region,
        "latitude": lat,
        "longitude": lon,
        "species": species,
        "latinName": latin_name,
    }
def clean_all(raw_records: list) -> dict:
    """Clean every record and remove duplicates.
    Returns the good records, plus counts of what was rejected and why."""
    cleaned = []
    rejected = []
    duplicates = 0
    seen_ids = set()
    seen_sightings = set()

    for raw in raw_records:
        try:
            record = clean_record(raw)
        except InvalidRecord as reason:
            rejected.append({"reason": str(reason), "record": raw})
            continue

        if record["id"] and record["id"] in seen_ids:
            duplicates += 1
            continue

        key = (record["date"], record["location"].lower(), record["species"].lower())
        if key in seen_sightings:
            duplicates += 1
            continue

        if record["id"]:
            seen_ids.add(record["id"])
        seen_sightings.add(key)
        cleaned.append(record)

    return {
        "cleaned": cleaned,
        "rejected": rejected,
        "duplicates_removed": duplicates,
    }
