
# tests/test_concurrency.py

import asyncio

import pytest

from app import processor


@pytest.mark.asyncio
async def test_concurrency_limit(monkeypatch):

    cities = [
        "New York",
        "Chicago",
        "Dallas",
        "Miami",
        "Seattle",
    ]

    monkeypatch.setattr(
        processor,
        "CITIES",
        cities,
    )

    monkeypatch.setattr(
        processor,
        "MAX_CONCURRENT_CITIES",
        2,
    )

    active = 0
    peak_active = 0

    async def fake_process_city(client, city, pool=None):

        nonlocal active, peak_active

        active += 1

        peak_active = max(
            peak_active,
            active,
        )

        try:
            # Simulate an asynchronous operation
            await asyncio.sleep(0.02)

            return {
                "city": city,
                "storage_status": "inserted",
            }

        finally:
            active -= 1

    monkeypatch.setattr(
        processor,
        "process_city",
        fake_process_city,
    )

    results, elapsed = await processor.run_concurrent(
        client=object(),
        pool=object(),
    )

    assert len(results) == 5
    assert elapsed >= 0

    # No more than two tasks were active
    assert peak_active <= 2

    # At least two overlapped
    assert peak_active == 2

    # All tasks completed
    assert active == 0

    # Results preserve input order
    assert [item["city"] for item in results] == cities
