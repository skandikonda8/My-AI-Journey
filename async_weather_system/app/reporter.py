
# app/reporter.py


def print_weather_report(results: list[dict]) -> None:

    print("\n========== WEATHER REPORT ==========")

    for result in results:

        if "error" in result:
            print(
                f"{result['city']}: FAILED - "
                f"{result['error']}"
            )
            continue

        print(f"\nCity: {result['city']}")
        print(f"Latitude: {result['latitude']}")
        print(f"Longitude: {result['longitude']}")

        print(
            f"Temperature: {result['temperature_c']} °C"
        )

        print(
            f"Humidity: {result['humidity_percent']} %"
        )

        print(
            f"Wind Speed: {result['wind_speed_kmh']} km/h"
        )

        print(f"Observed At: {result['observed_at']}")
        print(f"Collected At: {result['collected_at']}")

    print("\n====================================")


def print_performance_report(
    sequential_results: list[dict],
    concurrent_results: list[dict],
    sequential_time: float,
    concurrent_time: float,
) -> None:

    print("\n========== PERFORMANCE ==========")

    print(f"Sequential time: {sequential_time:.2f} seconds")
    print(f"Concurrent time: {concurrent_time:.2f} seconds")

    if concurrent_time > 0:
        speedup = sequential_time / concurrent_time
        print(f"Speedup: {speedup:.2f}x")

    sequential_success = sum(
        1 for result in sequential_results
        if "error" not in result
    )

    concurrent_success = sum(
        1 for result in concurrent_results
        if "error" not in result
    )

    print(
        f"Sequential successes: "
        f"{sequential_success}/{len(sequential_results)}"
    )

    print(
        f"Concurrent successes: "
        f"{concurrent_success}/{len(concurrent_results)}"
    )

    print("=================================")
