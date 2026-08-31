# Routes each AI touchpoint to the correct model.
# DeepSeek = judge only (content QA, not generation)
# Sonnet = generation for reports/dialogue (heavier reasoning)
# Haiku = short nudge generation (fast, cheap, templated text)

MODEL_BY_TOUCHPOINT = {
    "s9_nudge": "claude-haiku-4-5-20251001",
    "s10_nudge": "claude-haiku-4-5-20251001",
    "badge_explanation": "claude-haiku-4-5-20251001",
    "parent_report": "claude-sonnet-4-6",
    "avatar_dialogue": "claude-sonnet-4-6",
}

def get_model_for_touchpoint(touchpoint: str) -> str:
    if touchpoint not in MODEL_BY_TOUCHPOINT:
        raise ValueError(f"Unknown touchpoint: {touchpoint}")
    return MODEL_BY_TOUCHPOINT[touchpoint]