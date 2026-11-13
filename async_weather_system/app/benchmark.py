
# benchmark.py

import asyncio

import httpx

from app.config import REQUEST_TIMEOUT
from app.logging_config import setup_logging
from app.processor import (
    run_sequential,
    run_concurrent,
)


async def main():

    setup_logging()

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(REQUEST_TIMEOUT)
    ) as client:

        sequential_results, sequential_time = (
            await run_sequential(client)
        )

        # No pool supplied: concurrent read-only collection
        concurrent_results, concurrent_time = (
            await run_concurrent(client)
        )

    print("\n========== BENCHMARK ==========")

    print(
        f"Sequential: {sequential_time:.2f} seconds"
    )

    print(
        f"Concurrent: {concurrent_time:.2f} seconds"
    )

    if concurrent_time > 0:

        print(
            "Elapsed-time ratio: "
            f"{sequential_time / concurrent_time:.2f}x"
        )

    seq_successes = sum(
        "error" not in item
        for item in sequential_results
    )

    conc_successes = sum(
        "error" not in item
        for item in concurrent_results
    )

    print(
        f"Sequential successes: {seq_successes}"
    )

    print(
        f"Concurrent successes: {conc_successes}"
    )

    print("===============================")


if __name__ == "__main__":
    asyncio.run(main())
