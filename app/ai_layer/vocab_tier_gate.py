# 🔗 DATA SCIENCE HANDOFF — waiting on DS1.1's real vocabulary-tier map.
# Placeholder tiers below. Swap VOCAB_TIER_MAP with DS's real data once
# delivered — nothing else in this file should need to change.

VOCAB_TIER_MAP = {
    "cash": 0, "spend": 0, "save": 0, "price": 0,
    "profit": 1, "budget": 1, "customer": 1,
    "marginal cost": 2, "interest": 2,
    "capital": 3, "collateral": 3,
}

MAX_ALLOWED_TIER_BY_LEVEL = {1: 1, 2: 2, 3: 2}

def check_word_allowed(word: str, level: int) -> bool:
    tier = VOCAB_TIER_MAP.get(word.lower())
    if tier is None:
        return True
    return tier <= MAX_ALLOWED_TIER_BY_LEVEL.get(level, 1)