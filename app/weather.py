"""Weather lookup via a public HTTP API, with retry/backoff and timeouts."""

from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings

# Minimal city -> lat/lon table so the demo needs no geocoding service.
_CITIES = {
    "pune": (18.52, 73.86),
    "mumbai": (19.08, 72.88),
    "london": (51.51, -0.13),
    "new york": (40.71, -74.01),
    "san francisco": (37.77, -122.42),
}


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(4),
    reraise=True,
)
def get_weather(city: str) -> dict:
    """Return current weather for a known city.

    Raises ValueError for an unknown city; network errors are retried.
    """
    key = city.strip().lower()
    if key not in _CITIES:
        raise ValueError(f"Unknown city: {city}. Known: {', '.join(sorted(_CITIES))}")

    lat, lon = _CITIES[key]
    settings = get_settings()
    resp = httpx.get(
        settings.weather_api_url,
        params={"latitude": lat, "longitude": lon, "current_weather": True},
        timeout=10.0,
    )
    resp.raise_for_status()
    current = resp.json().get("current_weather", {})
    return {
        "city": city,
        "temperature_c": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
    }
