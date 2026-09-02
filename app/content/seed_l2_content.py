# Run this once Supabase access is confirmed — populates answer_bank
# with L2 nudge/badge content using the existing content pipeline.
# ⚠ Placeholder structured_input examples below — swap with DS's real
# L2 content briefs once delivered (per doc's "DS: L2 content" dependency).

from app.ai_layer.content_pipeline import generate_and_store_content

L2_CONTENT_JOBS = [
    {
        "touchpoint": "s9_nudge",
        "structured_input": {"location": "park_sidewalk", "level": 2, "traffic_tier": "medium"},
    },
    {
        "touchpoint": "s10_nudge",
        "structured_input": {"time_weather": "sunny_morning", "level": 2, "traffic_tier": "high"},
    },
    {
        "touchpoint": "badge_explanation",
        "structured_input": {"level": 2, "outcome": "profit", "badge": "smart_pricer"},
    },
]

def run_l2_content_seed():
    results = []
    for job in L2_CONTENT_JOBS:
        result = generate_and_store_content(
            touchpoint=job["touchpoint"],
            structured_input=job["structured_input"],
            level=2,
        )
        results.append({**job, "result": result})
    return results

if __name__ == "__main__":
    for r in run_l2_content_seed():
        print(r)