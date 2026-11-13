
# tests/test_api_client.py

import httpx
import pytest

from app.api_client import (
    get_coordinates,
    get_weather,
)


# Sample API response data
LOCATION_JSON = {
    "results": [
        {
            "name": "New York",
            "latitude": 40.71427,
            "longitude": -74.00597,
            "country": "United States",
        }
    ]
}

WEATHER_JSON = {
    "current": {
        "time": "2026-11-13T15:00",
        "temperature_2m": 15.5,
        "relative_humidity_2m": 65,
        "wind_speed_10m": 12.3,
    },
    "current_units": {
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "wind_speed_10m": "km/h",
    },
}


@pytest.mark.asyncio
async def test_geocoding_and_weather_api():

    # A fake HTTP server response handler
    def handler(request: httpx.Request):

        if "geocoding-api" in request.url.host:
            return httpx.Response(
                200,
                json=LOCATION_JSON,
            )

        if "api.open-meteo.com" == request.url.host:
            return httpx.Response(
                200,
                json=WEATHER_JSON,
            )

        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport
    ) as client:

        # ACT: Call our REAL application functions
        location = await get_coordinates(
            client, "New York"
        )

        weather = await get_weather(
            client,
            location.latitude,
            location.longitude,
        )

    # ASSERT
    assert location.name == "New York"
    assert location.latitude == 40.71427

    assert weather.temperature_2m == 15.5
    assert weather.relative_humidity_2m == 65
    assert weather.wind_speed_10m == 12.3


@pytest.mark.asyncio
async def test_weather_api_recovers_from_503():

    attempts = 0

    def handler(request: httpx.Request):

        nonlocal attempts
        attempts += 1

        # First request fails temporarily
        if attempts == 1:
            return httpx.Response(503)

        # Second request succeeds
        return httpx.Response(
            200,
            json=WEATHER_JSON,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport
    ) as client:

        weather = await get_weather(
            client,
            40.71427,
            -74.00597,
        )

    assert attempts == 2
    assert weather.temperature_2m == 15.5


@pytest.mark.asyncio
async def test_weather_api_does_not_retry_404():

    attempts = 0

    def handler(request: httpx.Request):

        nonlocal attempts
        attempts += 1

        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport
    ) as client:

        with pytest.raises(httpx.HTTPStatusError):

            await get_weather(
                client,
                40.71427,
                -74.00597,
            )

    assert attempts == 1
