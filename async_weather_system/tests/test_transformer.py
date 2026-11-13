
# tests/test_transformer.py

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import Location, CurrentWeather
from app.transformer import transform_weather


def test_transform_weather():

    # ARRANGE: Prepare known inputs
    location = Location(
        name="New York",
        latitude=40.71427,
        longitude=-74.00597,
        country="United States",
    )

    weather = CurrentWeather(
        time="2026-11-13T15:00",
        temperature_2m=15.5,
        relative_humidity_2m=65,
        wind_speed_10m=12.3,
    )

    # ACT: Execute the transformation
    record = transform_weather(
        city="New York",
        location=location,
        weather=weather,
    )

    # ASSERT: Check our expected output
    assert record.city == "New York"

    assert record.temperature_c == 15.5
    assert record.humidity_percent == 65
    assert record.wind_speed_kmh == 12.3

    assert record.latitude == 40.71427
    assert record.longitude == -74.00597

    assert record.observed_at == datetime(
        2026, 11, 13, 15, 0,
        tzinfo=timezone.utc,
    )

    assert record.collected_at.tzinfo is not None


def test_invalid_humidity_is_rejected():

    # ARRANGE / ACT / ASSERT
    with pytest.raises(ValidationError):

        CurrentWeather(
            time="2026-11-13T15:00",
            temperature_2m=15.5,
            relative_humidity_2m=250,
            wind_speed_10m=12.3,
        )
