from app.engine.backtest import build_scenarios, run_backtest, run_level_backtest
from app.engine.constants import get_level_constants


def test_level_one_backtest_covers_the_full_scenario_matrix():
    quantities = (10, 20, 40)
    constants = get_level_constants(1)
    scenarios = build_scenarios(level=1, quantities=quantities)

    expected_count = (
        len(quantities)
        * 2
        * len(constants["price_stops_cents"])
        * len(constants["base_traffic"])
        * len(constants["time_weather_multiplier"])
        * len(constants["advertising"])
    )

    assert len(scenarios) == expected_count
    assert {scenario["level"] for scenario in scenarios} == {1}
    assert {scenario["sourcing_method"] for scenario in scenarios} == {"buy", "make"}
    assert {scenario["quantity"] for scenario in scenarios} == set(quantities)


def test_level_one_backtest_is_repeatable():
    first = run_level_backtest(level=1, quantities=(10, 20))
    second = run_level_backtest(level=1, quantities=(10, 20))

    assert first == second


def test_level_one_backtest_returns_balance_metrics():
    report = run_level_backtest(level=1, quantities=(10, 20, 40))

    assert report["scenario_count"] == 3 * 2 * 8 * 3 * 4 * 3
    assert report["minimum_profit_cents"] <= report["average_profit_cents"]
    assert report["average_profit_cents"] <= report["maximum_profit_cents"]
    assert 0.0 <= report["profitable_run_rate"] <= 1.0
    assert 0.0 <= report["sell_through_rate"] <= 1.0
    assert all(result["units_sold"] <= quantity for result, quantity in zip(
        report["results"], (scenario["quantity"] for scenario in build_scenarios(1))
    ))


def test_backtest_accepts_a_small_custom_scenario_set():
    scenarios = build_scenarios(level=1, quantities=(20,))[:3]

    report = run_backtest(scenarios)

    assert report["scenario_count"] == 3
    assert len(report["results"]) == 3
