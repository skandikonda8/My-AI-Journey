
-- sql/schema.sql

CREATE TABLE IF NOT EXISTS public.weather_observations (

    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    city TEXT NOT NULL,

    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,

    temperature_c DOUBLE PRECISION NOT NULL,
    humidity_percent DOUBLE PRECISION NOT NULL,
    wind_speed_kmh DOUBLE PRECISION NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL,

    collected_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT city_not_blank
        CHECK (length(trim(city)) > 0),

    CONSTRAINT valid_latitude
        CHECK (
            latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT valid_longitude
        CHECK (
            longitude BETWEEN -180 AND 180
        ),

    CONSTRAINT valid_temperature
        CHECK (
            temperature_c > '-Infinity'::double precision
            AND temperature_c < 'Infinity'::double precision
        ),

    CONSTRAINT valid_humidity
        CHECK (
            humidity_percent BETWEEN 0 AND 100
        ),

    CONSTRAINT valid_wind_speed
        CHECK (
            wind_speed_kmh >= 0
            AND wind_speed_kmh < 'Infinity'::double precision
        ),

    CONSTRAINT unique_city_observation
        UNIQUE (city, observed_at)
);
