from app.engine.constants import get_level_constants

def calculate_flavor_cost(flavors: list, level: int) -> int:
    return len(flavors) * get_level_constants(level)["flavor_cost_cents"]

def calculate_sourcing_cost(quantity: int, method: str, level: int) -> int:
    return quantity * get_level_constants(level)["sourcing_cost_per_unit_cents"][method]

def calculate_total_cost(quantity: int, flavors: list, sourcing_method: str, level: int) -> int:
    return calculate_flavor_cost(flavors, level) + calculate_sourcing_cost(quantity, sourcing_method, level)

def resolve_price(price_slot: int, level: int) -> int:
    stops = get_level_constants(level)["price_stops_cents"]
    if price_slot < 0 or price_slot >= len(stops):
        raise ValueError(f"Invalid price slot: {price_slot}")
    return stops[price_slot]