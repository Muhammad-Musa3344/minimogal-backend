from app.engine.constants import get_level_constants

def calculate_units_sold(effective_traffic: int, price_slot: int, quantity_available: int, level: int) -> int:
    conversion_rate = get_level_constants(level)["conversion_rate_by_price_slot"][price_slot]
    demand = round(effective_traffic * conversion_rate)
    return min(demand, quantity_available)

def calculate_revenue(units_sold: int, price_cents: int) -> int:
    return units_sold * price_cents

def calculate_profit(revenue_cents: int, total_cost_cents: int) -> int:
    return revenue_cents - total_cost_cents

def get_vignette_customer_indices(quantity: int, level: int) -> list:
    count = get_level_constants(level)["vignette_customer_count"]
    step = quantity // (count + 1)
    return [step * (i + 1) for i in range(count)]

def get_difficulty_event_index(level: int) -> int:
    return get_level_constants(level)["difficulty_event_trigger_index"]