from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Query

from app.data_check import check_data
from app.elanco_client import fetch_sightings
from app.search import paginate, search_sightings
from app.stats import count_by, trend
from app.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: load the data.
    store.refresh()
    yield  # the app runs here


app = FastAPI(title="UK Tick Sightings API", lifespan=lifespan)


# ---------------------------------------------------------------- system

@app.get("/health")
def health():
    """Is the API working, and how fresh is the data?"""
    return {
        "status": "ok",
        "sightings_loaded": len(store.sightings),
        "last_updated": store.last_updated,
        "last_error": store.last_error,
    }


@app.post("/refresh")
def refresh():
    """Re-download the data from Elanco."""
    ok = store.refresh()
    return {
        "success": ok,
        "sightings_loaded": len(store.sightings),
        "error": store.last_error,
    }


@app.get("/data-quality")
def data_quality():
    """What the cleaning found: rejected records and duplicates."""
    return {
        "cleaned_records": len(store.sightings),
        "duplicates_removed": store.duplicates_removed,
        "rejected": len(store.rejected),
        "rejected_examples": store.rejected[:5],
    }


@app.get("/data-check")
def data_check():
    """Profile of the raw data straight from Elanco."""
    return check_data(fetch_sightings())


# ---------------------------------------------------------------- search

def filtered(start_date, end_date, location, region, species):
    """Apply the search filters, with a clear error for a bad date range."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    return search_sightings(
        store.sightings,
        start_date=start_date,
        end_date=end_date,
        location=location,
        region=region,
        species=species,
    )


@app.get("/sightings")
def get_sightings(
    start_date: date | None = Query(None, description="From this day, e.g. 2020-01-01"),
    end_date: date | None = Query(None, description="Up to this day, e.g. 2020-12-31"),
    location: str | None = Query(None, description="City, e.g. London"),
    region: str | None = Query(None, description="UK region, e.g. Scotland"),
    species: str | None = Query(None, description="e.g. Marsh tick"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    """Search and filter sightings by time range and location."""
    results = filtered(start_date, end_date, location, region, species)
    return paginate(results, page, page_size)


# ---------------------------------------------------------------- stats

@app.get("/stats/regions")
def stats_regions(
    start_date: date | None = None,
    end_date: date | None = None,
    species: str | None = None,
):
    """Number of sightings per UK region."""
    return count_by(filtered(start_date, end_date, None, None, species), "region")


@app.get("/stats/species")
def stats_species(
    start_date: date | None = None,
    end_date: date | None = None,
    location: str | None = None,
    region: str | None = None,
):
    """Number of sightings per species."""
    return count_by(filtered(start_date, end_date, location, region, None), "species")


@app.get("/stats/trends")
def stats_trends(
    interval: str = Query("month", pattern="^(week|month)$", description="week or month"),
    start_date: date | None = None,
    end_date: date | None = None,
    location: str | None = None,
    region: str | None = None,
    species: str | None = None,
):
    """Sightings over time, grouped by week or month."""
    sightings = filtered(start_date, end_date, location, region, species)
    return {"interval": interval, "points": trend(sightings, interval)}