
# app/transformer.py

from datetime import datetime, timezone

from app.models import (
    Location,
    CurrentWeather,
    WeatherRecord,
)


def transform_weather(
    city: str,
    location: Location,
    weather: CurrentWeather,
) -> WeatherRecord:

    # 1. Read the source observation timestamp
    observed_at = weather.time

    # 2. Normalize observation time to UTC
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )
    else:
        observed_at = observed_at.astimezone(
            timezone.utc
        )

    # 3. Record when our system processed it
    collected_at = datetime.now(timezone.utc)

    # 4. Build our standardized record
    record = WeatherRecord(
        city=city,
        latitude=location.latitude,
        longitude=location.longitude,
        temperature_c=weather.temperature_2m,
        humidity_percent=weather.relative_humidity_2m,
        wind_speed_kmh=weather.wind_speed_10m,
        observed_at=observed_at,
        collected_at=collected_at,
    )

    # 5. Return the validated internal record
    return record
