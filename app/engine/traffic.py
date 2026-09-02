from app.engine.constants import get_level_constants

def get_base_traffic(location: str, level: int) -> int:
    return get_level_constants(level)["base_traffic"][location]

def calculate_effective_traffic(location: str, time_weather: str, advertising: str, level: int) -> int:
    consts = get_level_constants(level)
    base = consts["base_traffic"][location]
    time_multiplier = consts["time_weather_multiplier"][time_weather]
    ad_multiplier = consts["advertising"][advertising]["multiplier"]
    return round(base * time_multiplier * ad_multiplier)