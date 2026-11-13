
# app/database.py

import asyncio
import logging

import asyncpg

from app.config import (
    DB_NAME,
    DB_USER,
    DB_HOST,
    DB_PASSWORD,
    DB_POOL_MIN,
    DB_POOL_MAX,
    DB_ACQUIRE_TIMEOUT,
    DB_COMMAND_TIMEOUT,
)

from app.models import WeatherRecord
from app.retry import retry_async


logger = logging.getLogger(__name__)


def create_database_pool():

    return asyncpg.create_pool(
        database=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        password=DB_PASSWORD,
        min_size=DB_POOL_MIN,
        max_size=DB_POOL_MAX,
        command_timeout=DB_COMMAND_TIMEOUT,
    )


def should_retry_database(error: Exception) -> bool:

    return isinstance(
        error,
        (
            asyncpg.PostgresConnectionError,
            OSError,
            asyncio.TimeoutError,
        ),
    )


async def save_weather_record(
    pool: asyncpg.Pool,
    record: WeatherRecord,
) -> int | None:

    query = """
        INSERT INTO public.weather_observations (
            city,
            latitude,
            longitude,
            temperature_c,
            humidity_percent,
            wind_speed_kmh,
            observed_at,
            collected_at
        )
        VALUES (
            $1, $2, $3, $4,
            $5, $6, $7, $8
        )
        ON CONFLICT (city, observed_at)
        DO NOTHING
        RETURNING id;
    """

    async def perform_insert():

        async with pool.acquire(
            timeout=DB_ACQUIRE_TIMEOUT
        ) as connection:

            row_id = await connection.fetchval(
                query,
                record.city,
                record.latitude,
                record.longitude,
                record.temperature_c,
                record.humidity_percent,
                record.wind_speed_kmh,
                record.observed_at,
                record.collected_at,
            )

            return row_id

    logger.debug(
        "city=%s event=database_insert_started",
        record.city,
    )

    row_id = await retry_async(
        perform_insert,
        operation_name=f"database_insert:{record.city}",
        should_retry=should_retry_database,
    )

    if row_id is None:

        logger.info(
            "city=%s event=duplicate_skipped",
            record.city,
        )

    else:

        logger.info(
            "city=%s event=database_inserted id=%s",
            record.city,
            row_id,
        )

    return row_id


async def count_weather_records(
    pool: asyncpg.Pool,
) -> int:

    async with pool.acquire(
        timeout=DB_ACQUIRE_TIMEOUT
    ) as connection:

        return await connection.fetchval(
            "SELECT COUNT(*) "
            "FROM public.weather_observations"
        )
