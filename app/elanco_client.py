
import httpx

ELANCO_URL = "https://dev-task.elancoapps.com/data/tick-sightings"

class ElancoAPIError(Exception):
    """Custom exception for Elanco API errors."""

def fetch_sightings() -> list[dict]:
    """Fetch tick sightings from the Elanco API."""
    try:
        response = httpx.get(ELANCO_URL, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Assuming the API returns JSON data
    except httpx.HTTPStatusError as e:
        raise ElancoAPIError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
    except httpx.RequestError as e:
        raise ElancoAPIError(f"An error occurred while requesting data: {e}")
    except ValueError as e:
        raise ElancoAPIError(f"Error parsing JSON response: {e}")
            