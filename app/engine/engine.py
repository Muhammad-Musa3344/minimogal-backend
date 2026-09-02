from app.engine.seed import generate_seed
from app.engine.pricing import calculate_total_cost, resolve_price
from app.engine.traffic import calculate_effective_traffic, get_base_traffic
from app.engine.simulation import (
    calculate_units_sold,
    calculate_revenue,
    calculate_profit,
    get_vignette_customer_indices,
    get_difficulty_event_index,
)

def run_engine(
    avatar_id: str,
    playthrough_index: int,
    quantity: int,
    flavors: list,
    sourcing_method: str,
    price_slot: int,
    location: str,
    time_weather: str,
    advertising: str,
    level: int = 1,
) -> dict:
    seed = generate_seed(avatar_id, playthrough_index)
    total_cost = calculate_total_cost(quantity, flavors, sourcing_method, level)
    price = resolve_price(price_slot, level)

    base_traffic = get_base_traffic(location, level)
    effective_traffic = calculate_effective_traffic(location, time_weather, advertising, level)

    units_sold = calculate_units_sold(effective_traffic, price_slot, quantity, level)
    revenue = calculate_revenue(units_sold, price)
    profit = calculate_profit(revenue, total_cost)

    return {
        "seed": seed,
        "level": level,
        "total_cost": total_cost,
        "price": price,
        "base_traffic": base_traffic,
        "effective_traffic": effective_traffic,
        "units_sold": units_sold,
        "revenue": revenue,
        "profit": profit,
        "outcome": "profit" if profit >= 0 else "loss",
        "vignette_customer_indices": get_vignette_customer_indices(quantity, level),
        "difficulty_event_index": get_difficulty_event_index(level),
    }