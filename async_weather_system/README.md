
# Async Weather Monitoring System

An asynchronous Python backend application that collects
current weather data for multiple US cities, validates and
transforms API responses, and stores observations in PostgreSQL.

## Features

- Asynchronous geocoding and weather API integration
- Concurrent processing with configurable limits
- Pydantic validation of external responses
- Standardized internal WeatherRecord model
- PostgreSQL storage using asyncpg
- Connection pooling and parameterized SQL
- Duplicate observation handling
- Timeouts, selective retries, and exponential backoff
- UTC-aware timestamps
- Logging and error isolation
- Unit and database integration tests

## Technology Stack

- Python 3.10+
- asyncio
- HTTPX
- Pydantic v2
- PostgreSQL
- asyncpg
- pytest
- pytest-asyncio

## Project Structure

app/
  api_client.py       HTTP communication
  config.py           Settings
  database.py         PostgreSQL operations
  logging_config.py   Logging configuration
  models.py           Data validation and models
  processor.py        Workflow orchestration
  reporter.py         Output formatting
  retry.py            Retry logic
  transformer.py      Data transformation

sql/
  schema.sql          Initial database schema

tests/
  test_transformer.py
  test_api_client.py
  test_processor.py
  test_database.py
  test_concurrency.py

main.py               Application entry point
benchmark.py          Optional read-only benchmark

## Architecture

City
  -> Geocoding API
  -> Location validation
  -> Weather API
  -> Weather validation
  -> WeatherRecord transformation
  -> PostgreSQL insert / duplicate handling
  -> Final report

Each city is processed asynchronously.

A semaphore limits how many city workflows can run at once.

## Setup

### 1. Create and activate a Python environment

python3 -m venv .venv
source .venv/bin/activate

### 2. Install dependencies

python -m pip install -r requirements-dev.txt

### 3. Create PostgreSQL database

createdb weather_monitoring

### 4. Create the table

psql -d weather_monitoring -v ON_ERROR_STOP=1 -f sql/schema.sql

### 5. Configure database access

By default, the local setup uses:
- Database: weather_monitoring
- PostgreSQL user: current OS username
- Local Unix socket connection

Optional environment variables:
- DB_NAME
- DB_USER
- DB_HOST
- DB_PASSWORD

Do not commit database passwords.

### 6. Run the application

python main.py

## Testing

Run unit and mocked API tests:

python -m pytest -q

Database integration tests require a separate database.

Create the test database:

createdb weather_monitoring_test

Create its table:

psql -d weather_monitoring_test -v ON_ERROR_STOP=1 -f sql/schema.sql

Run all tests including database integration:

RUN_DB_TESTS=1 DB_NAME=weather_monitoring_test python -m pytest -q

## Optional Benchmark

python benchmark.py

Compares sequential and concurrency-limited data collection
without database writes.

## Database Table

public.weather_observations

Important columns:
- id
- city
- latitude
- longitude
- temperature_c
- humidity_percent
- wind_speed_kmh
- observed_at
- collected_at

Unique observation key:
(city, observed_at)

## Error Handling

Transient HTTP and selected database connection failures
are retried with bounded exponential backoff and jitter.

Validation failures and non-retryable errors are reported
without blindly repeating the operation.

Expected city-level errors are isolated so other cities
can continue processing.

## Logging

Console: INFO and above

logs/weather.log: DEBUG and above

Log files rotate automatically.

## Current Limitations

- The application runs when invoked; no scheduler is included.
- Current results are collected from Open-Meteo.
- The database uses city + observation timestamp for uniqueness.
- There is no REST API or web dashboard.
- Retries do not yet handle every provider rate-limit scenario.
- Database migrations and monitoring alerts are not included.
- A single run is not a rigorous performance benchmark.

## Future Enhancements

- Scheduled collection
- FastAPI endpoints
- Monitoring dashboards
- Metrics and alerts
- Database migrations
- API response caching
- Deployment with Docker
- Additional weather providers
