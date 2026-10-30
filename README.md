# UK Tick Sightings – Backend

Ayush Majumder – Elanco Placement Programme 2026, Backend task

A Python (FastAPI) backend that downloads tick sightings from the
[Elanco API](https://dev-task.elancoapps.com/), cleans them, and provides
endpoints to search, filter and report on them.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** to try every endpoint.

## Endpoints

- `GET /sightings` – search by `start_date`, `end_date`, `location`, `region`, `species` (paginated)
- `GET /stats/regions` – sightings per UK region
- `GET /stats/species` – sightings per species
- `GET /stats/trends?interval=week|month` – sightings over time
- `GET /health` – status and when the data was last loaded
- `POST /refresh` – reload data from Elanco
- `GET /data-check`, `GET /data-quality` – data quality reports

## Choices

- **FastAPI** – validates input automatically and generates the `/docs` page.
- **Profiled the data first** (`/data-check`). The 1,000 records are currently clean, but because
  the data is crowdsourced, the cleaning step still rejects records with missing or invalid dates,
  locations or species, tidies spacing and capitals, and removes duplicates (same id, or same
  date, place and species).
- **Added UK regions** – the API only gives cities, so each city is mapped to a region.
- **Data kept in memory** – loaded once at startup, so the API is fast and keeps working
  if Elanco's API is down. For larger data I'd use a database.

## Error handling

- Elanco API failures (timeout, no connection, 429, 500, bad JSON) give a clear error, not a crash.
- If a refresh fails, the last good data is still served.
- Invalid input (e.g. start date after end date) returns a clear `400` error.

## With more time

Automatic retries, a database, automated tests, scheduled refreshes, and insights
such as areas with rising tick activity.