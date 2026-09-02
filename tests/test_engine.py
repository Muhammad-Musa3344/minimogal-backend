from app.engine.engine import run_engine

def test_l1_deterministic():
    inputs = dict(
        avatar_id="avatar1", playthrough_index=0, quantity=20,
        flavors=["Grape", "Cherry"], sourcing_method="make",
        price_slot=4, location="park_sidewalk",
        time_weather="sunny_morning", advertising="sign", level=1,
    )
    result1 = run_engine(**inputs)
    result2 = run_engine(**inputs)
    assert result1 == result2, "L1 engine must be deterministic"

def test_l2_deterministic():
    inputs = dict(
        avatar_id="avatar1", playthrough_index=0, quantity=25,
        flavors=["Grape", "Cherry", "Orange"], sourcing_method="make",
        price_slot=5, location="park_sidewalk",
        time_weather="sunny_morning", advertising="sign", level=2,
    )
    result1 = run_engine(**inputs)
    result2 = run_engine(**inputs)
    assert result1 == result2, "L2 engine must be deterministic"

def test_l2_generalizes_pattern():
    """Proves the engine design works past L1 without code changes —
    only constants.py differs between levels."""
    result = run_engine(
        avatar_id="avatar1", playthrough_index=0, quantity=25,
        flavors=["Grape"], sourcing_method="buy",
        price_slot=5, location="fair",
        time_weather="sunny_morning", advertising="sign", level=2,
    )
    assert result["level"] == 2
    assert result["outcome"] in ["profit", "loss"]
    assert isinstance(result["profit"], int)

def test_l1_and_l2_use_different_constants():
    """Same inputs, different level -> different total_cost, proving
    L2's constants are actually being read, not L1's leaking through."""
    common = dict(
        avatar_id="avatar1", playthrough_index=0, quantity=20,
        flavors=["Grape"], sourcing_method="buy",
        price_slot=3, location="park_sidewalk",
        time_weather="sunny_morning", advertising="sign",
    )
    l1_result = run_engine(**common, level=1)
    l2_result = run_engine(**common, level=2)
    assert l1_result["total_cost"] != l2_result["total_cost"]