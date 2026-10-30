
"""Keeps the cleaned sightings in memory so we don't call Elanco on every request."""
from datetime import datetime

from app.cleaning import clean_all
from app.elanco_client import ElancoAPIError, fetch_sightings


class SightingStore:
    def __init__(self):
        self.sightings = []          # the cleaned records
        self.rejected = []           # records we couldn't use, with reasons
        self.duplicates_removed = 0
        self.last_updated = None     # when we last loaded data successfully
        self.last_error = None       # the last thing that went wrong, if anything

    def refresh(self) -> bool:
        """Download and clean the data. Returns True if it worked."""
        try:
            raw = fetch_sightings()
        except ElancoAPIError as error:
            # Don't throw away the data we already have, just remember the error.
            self.last_error = str(error)
            return False

        result = clean_all(raw)
        self.sightings = result["cleaned"]
        self.rejected = result["rejected"]
        self.duplicates_removed = result["duplicates_removed"]
        self.last_updated = datetime.now()
        self.last_error = None
        return True


# One shared store for the whole app.
store = SightingStore()