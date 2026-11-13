
# app/models.py

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    AwareDatetime,
)


# 1. One location from the Geocoding API
class Location(BaseModel):
    name: str = Field(min_length=1)
    latitude: float = Field(
        ge=-90, le=90, allow_inf_nan=False
    )
    longitude: float = Field(
        ge=-180, le=180, allow_inf_nan=False
    )
    country: str = Field(min_length=1)
    admin1: str | None = None


# 2. Complete Geocoding API response
class GeocodingResponse(BaseModel):
    results: list[Location] = Field(
        default_factory=list
    )


# 3. Current Weather API measurements
class CurrentWeather(BaseModel):
    time: datetime

    temperature_2m: float = Field(
        allow_inf_nan=False
    )

    relative_humidity_2m: float = Field(
        ge=0, le=100, allow_inf_nan=False
    )

    wind_speed_10m: float = Field(
        ge=0, allow_inf_nan=False
    )


# 4. Expected weather units
class CurrentUnits(BaseModel):
    temperature_2m: Literal["°C"]
    relative_humidity_2m: Literal["%"]
    wind_speed_10m: Literal["km/h"]


# 5. Complete Weather API response
class WeatherResponse(BaseModel):
    current: CurrentWeather
    current_units: CurrentUnits


# 6. OUR OWN STANDARDIZED WEATHER RECORD
class WeatherRecord(BaseModel):
    city: str = Field(min_length=1)

    latitude: float = Field(
        ge=-90, le=90, allow_inf_nan=False
    )
    longitude: float = Field(
        ge=-180, le=180, allow_inf_nan=False
    )

    temperature_c: float = Field(
        allow_inf_nan=False
    )

    humidity_percent: float = Field(
        ge=0, le=100, allow_inf_nan=False
    )

    wind_speed_kmh: float = Field(
        ge=0, allow_inf_nan=False
    )

    observed_at: AwareDatetime
    collected_at: AwareDatetime
