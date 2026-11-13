
# tests/test_processor.py

import pytest

from app import processor
from app.models import Location, CurrentWeather


@pytest.mark.asyncio
async def test_one_city_failure_does_not_stop_others(
    monkeypatch,
):

    # Test only two cities
    monkeypatch.setattr(
        processor,
        "CITIES",
        ["New York", "Dallas"],
    )

    # Fake geocoding function
    async def fake_get_coordinates(client, city):

        return Location(
            name=city,
            latitude=40.0 if city == "New York" else 32.0,
            longitude=-74.0 if city == "New York" else -97.0,
            country="United States",
        )

    # Fake weather function
    async def fake_get_weather(
        client,
        latitude,
        longitude,
    ):

        if latitude == 32.0:
            raise ValueError(
                "Simulated Dallas weather failure"
            )

        return CurrentWeather(
            time="2026-11-13T15:00",
            temperature_2m=15.5,
            relative_humidity_2m=65,
            wind_speed_10m=12.3,
        )

    # Fake database insert
    async def fake_save_weather_record(pool, record):
        return 101

    # Replace dependencies ONLY during this test
    monkeypatch.setattr(
        processor,
        "get_coordinates",
        fake_get_coordinates,
    )

    monkeypatch.setattr(
        processor,
        "get_weather",
        fake_get_weather,
    )

    monkeypatch.setattr(
        processor,
        "save_weather_record",
        fake_save_weather_record,
    )

    # We aren't using a real client or pool.
    fake_client = object()
    fake_pool = object()

    # ACT
    results, elapsed = await processor.run_concurrent(
        fake_client,
        fake_pool,
    )

    # ASSERT
    assert len(results) == 2
    assert elapsed >= 0

    new_york = results[0]
    dallas = results[1]

    assert new_york["city"] == "New York"
    assert new_york["storage_status"] == "inserted"
    assert new_york["database_id"] == 101
    assert new_york["temperature_c"] == 15.5

    assert dallas["city"] == "Dallas"
    assert dallas["storage_status"] == "failed"
    assert "Simulated Dallas" in dallas["error"]
