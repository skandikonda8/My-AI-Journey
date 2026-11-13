
# main.py

import asyncio
import logging

import httpx

from app.config import REQUEST_TIMEOUT
from app.database import (
    create_database_pool,
    count_weather_records,
)
from app.logging_config import setup_logging
from app.processor import run_concurrent
from app.reporter import print_weather_report


def print_run_summary(
    results: list[dict],
    elapsed: float,
    before_count: int,
    after_count: int,
) -> None:

    inserted = sum(
        result.get("storage_status") == "inserted"
        for result in results
    )

    duplicates = sum(
        result.get("storage_status") == "duplicate"
        for result in results
    )

    failed = sum(
        result.get("storage_status") == "failed"
        for result in results
    )

    print("\n========== RUN SUMMARY ==========")
    print(f"Cities attempted: {len(results)}")
    print(f"New observations inserted: {inserted}")
    print(f"Duplicates skipped: {duplicates}")
    print(f"Failed workflows: {failed}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Database rows before: {before_count}")
    print(f"Database rows after: {after_count}")
    print("=================================")


async def main():

    setup_logging()

    logger = logging.getLogger(__name__)

    logger.info("event=application_started")

    try:
        timeout = httpx.Timeout(REQUEST_TIMEOUT)

        # Reuse one HTTP client across the run
        limits = httpx.Limits(
            max_connections=10,
            max_keepalive_connections=5,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
        ) as client:

            # Reuse one database connection pool
            async with create_database_pool() as pool:

                logger.info(
                    "event=database_pool_initialized"
                )

                before_count = (
                    await count_weather_records(pool)
                )

                # Collect + save once
                results, elapsed = await run_concurrent(
                    client,
                    pool,
                )

                after_count = (
                    await count_weather_records(pool)
                )

        print_weather_report(results)

        print_run_summary(
            results,
            elapsed,
            before_count,
            after_count,
        )

        logger.info(
            "event=application_completed "
            "elapsed_seconds=%.3f",
            elapsed,
        )

    except Exception:

        logger.exception(
            "event=application_failed"
        )

        raise


if __name__ == "__main__":
    asyncio.run(main())
