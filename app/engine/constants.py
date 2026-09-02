# 🔗 DATA SCIENCE HANDOFF — placeholder values until DS delivers real constants.
# Structured per-level so L2/L3 slot in later without changing engine code.

WALLET_MIN_CENTS = 2500
WALLET_MAX_CENTS = 10000

LEVEL_CONSTANTS = {
    1: {
        "flavor_cost_cents": 50,
        "sourcing_cost_per_unit_cents": {"buy": 15, "make": 5},
        "price_stops_cents": [25, 50, 75, 100, 125, 150, 175, 200],
        "price_optimum_slot": 4,
        "base_traffic": {"front_yard": 20, "park_sidewalk": 40, "fair": 70},
        "time_weather_multiplier": {
            "sunny_morning": 1.25, "cloudy_morning": 1.0,
            "sunny_afternoon": 1.1, "rainy_afternoon": 0.5,
        },
        "advertising": {
            "sign": {"cost_cents": 100, "multiplier": 1.3},
            "pamphlet": {"cost_cents": 50, "multiplier": 1.15},
            "skip": {"cost_cents": 0, "multiplier": 1.0},
        },
        "conversion_rate_by_price_slot": [0.30, 0.45, 0.60, 0.75, 0.85, 0.70, 0.50, 0.25],
        "vignette_customer_count": 3,
        "difficulty_event_trigger_index": 5,
    },
    # ⚠ PLACEHOLDER — waiting on DS's L2 constants (BE2.2). Same shape as L1,
    # numbers copied for now so the engine can be exercised at level=2;
    # swap these the moment DS delivers real L2 values.
    2: {
        "flavor_cost_cents": 50,
        "sourcing_cost_per_unit_cents": {"buy": 20, "make": 8},
        "price_stops_cents": [25, 50, 75, 100, 125, 150, 175, 200, 225, 250],
        "price_optimum_slot": 5,
        "base_traffic": {"front_yard": 25, "park_sidewalk": 50, "fair": 90},
        "time_weather_multiplier": {
            "sunny_morning": 1.25, "cloudy_morning": 1.0,
            "sunny_afternoon": 1.1, "rainy_afternoon": 0.5,
        },
        "advertising": {
            "sign": {"cost_cents": 150, "multiplier": 1.35},
            "pamphlet": {"cost_cents": 75, "multiplier": 1.2},
            "skip": {"cost_cents": 0, "multiplier": 1.0},
        },
        "conversion_rate_by_price_slot": [0.28, 0.42, 0.58, 0.72, 0.82, 0.78, 0.55, 0.35, 0.20, 0.10],
        "vignette_customer_count": 4,
        "difficulty_event_trigger_index": 6,
    },
}

def get_level_constants(level: int) -> dict:
    if level not in LEVEL_CONSTANTS:
        raise ValueError(f"No constants defined for level {level}")
    return LEVEL_CONSTANTS[level]