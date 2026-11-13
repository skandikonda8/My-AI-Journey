
# app/api_client.py

import logging

import httpx

from app.config import GEOCODING_URL, WEATHER_URL
from app.models import (
    Location,
    GeocodingResponse,
    CurrentWeather,
    WeatherResponse,
)
from app.retry import retry_async


logger = logging.getLogger(__name__)


# Status codes that may indicate temporary failures
RETRYABLE_STATUS_CODES = {
    408,
    429,
    500,
    502,
    503,
    504,
}


def should_retry_http(error: Exception) -> bool:

    # Timeouts and temporary network failures
    if isinstance(
        error,
        (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError,
        ),
    ):
        return True

    # Retry only selected HTTP error statuses
    if isinstance(error, httpx.HTTPStatusError):
        return (
            error.response.status_code
            in RETRYABLE_STATUS_CODES
        )

    return False


async def request_json(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
    operation_name: str,
) -> dict:

    async def perform_request():

        response = await client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response

    # Retry the HTTP operation if appropriate
    response = await retry_async(
        perform_request,
        operation_name=operation_name,
        should_retry=should_retry_http,
    )

    # Parse JSON after a successful HTTP response
    return response.json()


async def get_coordinates(
    client: httpx.AsyncClient,
    city: str,
) -> Location:

    logger.debug(
        "city=%s event=geocoding_request_started",
        city,
    )

    params = {
        "name": city,
        "count": 1,
        "countryCode": "US",
        "format": "json",
    }

    data = await request_json(
        client=client,
        url=GEOCODING_URL,
        params=params,
        operation_name=f"geocoding:{city}",
    )

    validated = GeocodingResponse.model_validate(data)

    if not validated.results:
        raise ValueError(
            f"No coordinates found for {city}"
        )

    location = validated.results[0]

    logger.debug(
        "city=%s event=geocoding_request_completed",
        city,
    )

    return location


async def get_weather(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
) -> CurrentWeather:

    logger.debug(
        "event=weather_request_started "
        "latitude=%s longitude=%s",
        latitude,
        longitude,
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "timezone": "UTC",
    }

    data = await request_json(
        client=client,
        url=WEATHER_URL,
        params=params,
        operation_name=(
            f"weather:{latitude},{longitude}"
        ),
    )

    validated = WeatherResponse.model_validate(data)

    logger.debug(
        "event=weather_request_completed "
        "latitude=%s longitude=%s",
        latitude,
        longitude,
    )

    return validated.current
