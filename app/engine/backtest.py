from itertools import product
from statistics import mean, median

from app.engine.constants import get_level_constants
from app.engine.engine import run_engine


def build_scenarios(level: int = 1, quantities: tuple[int, ...] = (10, 20, 40)) -> list[dict]:
    """Build a complete deterministic scenario matrix for one level."""
    constants = get_level_constants(level)
    scenario_values = product(
        quantities,
        ("buy", "make"),
        range(len(constants["price_stops_cents"])),
        constants["base_traffic"],
        constants["time_weather_multiplier"],
        constants["advertising"],
    )

    return [
        {
            "avatar_id": "backtest",
            "playthrough_index": index,
            "quantity": quantity,
            "flavors": ["Grape"],
            "sourcing_method": sourcing_method,
            "price_slot": price_slot,
            "location": location,
            "time_weather": time_weather,
            "advertising": advertising,
            "level": level,
        }
        for index, (
            quantity,
            sourcing_method,
            price_slot,
            location,
            time_weather,
            advertising,
        ) in enumerate(scenario_values)
    ]


def run_backtest(scenarios: list[dict]) -> dict:
    """Run scenarios and return results together with balance-oriented metrics."""
    results = [run_engine(**scenario) for scenario in scenarios]
    profits = [result["profit"] for result in results]
    quantities = [scenario["quantity"] for scenario in scenarios]
    total_units_available = sum(quantities)
    total_units_sold = sum(result["units_sold"] for result in results)
    profitable_runs = sum(result["outcome"] == "profit" for result in results)

    return {
        "scenario_count": len(results),
        "results": results,
        "profitable_run_rate": profitable_runs / len(results) if results else 0.0,
        "average_profit_cents": mean(profits) if profits else 0.0,
        "median_profit_cents": median(profits) if profits else 0.0,
        "minimum_profit_cents": min(profits) if profits else 0,
        "maximum_profit_cents": max(profits) if profits else 0,
        "sell_through_rate": (
            total_units_sold / total_units_available
            if total_units_available
            else 0.0
        ),
    }


def run_level_backtest(
    level: int = 1, quantities: tuple[int, ...] = (10, 20, 40)
) -> dict:
    """Run the standard scenario matrix for a level."""
    return run_backtest(build_scenarios(level, quantities))
