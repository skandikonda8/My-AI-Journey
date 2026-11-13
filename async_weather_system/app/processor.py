
# app/processor.py

import asyncio
import logging
import time

import asyncpg
import httpx
from pydantic import ValidationError

from app.api_client import get_coordinates, get_weather
from app.config import CITIES, MAX_CONCURRENT_CITIES
from app.database import save_weather_record
from app.transformer import transform_weather


logger = logging.getLogger(__name__)


# Process ONE city from start to finish
async def process_city(
    client: httpx.AsyncClient,
    city: str,
    pool: asyncpg.Pool | None = None,
) -> dict:

    stage = "starting"

    logger.info(
        "city=%s event=processing_started",
        city,
    )

    try:
        # 1. Fetch and validate location
        stage = "geocoding"

        location = await get_coordinates(
            client,
            city,
        )

        # 2. Fetch and validate weather
        stage = "weather"

        weather = await get_weather(
            client,
            location.latitude,
            location.longitude,
        )

        # 3. Transform into WeatherRecord
        stage = "transformation"

        record = transform_weather(
            city=city,
            location=location,
            weather=weather,
        )

        logger.debug(
            "city=%s event=transformation_completed",
            city,
        )

        # 4. Save if a database pool was supplied
        database_id = None
        storage_status = "not_requested"

        if pool is not None:

            stage = "database"

            database_id = await save_weather_record(
                pool,
                record,
            )

            if database_id is None:
                storage_status = "duplicate"
            else:
                storage_status = "inserted"

        # 5. Prepare result for reporting
        result = record.model_dump(mode="json")

        result["database_id"] = database_id
        result["storage_status"] = storage_status

        logger.info(
            "city=%s event=processing_completed "
            "storage_status=%s",
            city,
            storage_status,
        )

        return result

    except (
        httpx.HTTPError,
        asyncpg.PostgresError,
        OSError,
        TimeoutError,
        ValidationError,
        ValueError,
        KeyError,
        TypeError,
    ) as error:

        logger.exception(
            "city=%s event=processing_failed "
            "stage=%s error_type=%s",
            city,
            stage,
            type(error).__name__,
        )

        return {
            "city": city,
            "error": str(error),
            "storage_status": "failed",
        }


# Sequential mode for optional benchmarking
async def run_sequential(
    client: httpx.AsyncClient,
) -> tuple[list[dict], float]:

    logger.info("event=sequential_run_started")

    start = time.perf_counter()
    results = []

    for city in CITIES:

        result = await process_city(
            client,
            city,
        )

        results.append(result)

    elapsed = time.perf_counter() - start

    logger.info(
        "event=sequential_run_completed "
        "elapsed_seconds=%.3f",
        elapsed,
    )

    return results, elapsed


# Concurrent mode with a limit
async def run_concurrent(
    client: httpx.AsyncClient,
    pool: asyncpg.Pool | None = None,
) -> tuple[list[dict], float]:

    if MAX_CONCURRENT_CITIES < 1:
        raise ValueError(
            "MAX_CONCURRENT_CITIES must be at least 1"
        )

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_CITIES
    )

    async def run_limited_city(city: str) -> dict:

        logger.debug(
            "city=%s event=waiting_for_slot",
            city,
        )

        async with semaphore:

            logger.debug(
                "city=%s event=slot_acquired",
                city,
            )

            return await process_city(
                client,
                city,
                pool,
            )

    logger.info(
        "event=concurrent_run_started "
        "city_count=%s concurrency_limit=%s",
        len(CITIES),
        MAX_CONCURRENT_CITIES,
    )

    start = time.perf_counter()

    tasks = [
        run_limited_city(city)
        for city in CITIES
    ]

    results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    logger.info(
        "event=concurrent_run_completed "
        "elapsed_seconds=%.3f",
        elapsed,
    )

    return results, elapsed
