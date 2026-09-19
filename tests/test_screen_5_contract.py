# tests/test_screen_5_contract.py
"""
Unit tests for Screen 5 Pydantic schema contracts and mock provider.
Validates serialization, field constraints, validation errors, and level-based behavior.
"""

import pytest
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.screen_5 import (
    FlavorOption,
    QuantityOption,
    NudgeRule,
    Screen5OptionsResponse,
    Screen5DecisionRequest,
    Screen5PersistedPayload,
    Screen5DecisionResponse,
    MockFlavorQuantityProvider,
)


def test_mock_provider_levels():
    """Verify that MockFlavorQuantityProvider returns distinct level-tailored data."""
    for level in [1, 2, 3]:
        data = MockFlavorQuantityProvider.get_options_for_level(level)
        assert len(data["flavors"]) >= 3
        assert len(data["quantities"]) == 3
        assert data["max_flavors"] in [2, 3, 4]
        assert len(data["nudges"]) >= 1


def test_options_response_serialization():
    """Verify Screen5OptionsResponse serializes cleanly with all child models."""
    session_id = uuid4()
    options_data = MockFlavorQuantityProvider.get_options_for_level(1)

    response = Screen5OptionsResponse(
        kid_session_id=session_id,
        level=1,
        wallet_balance_cents=5000,
        max_flavors_allowed=options_data["max_flavors"],
        flavor_options=options_data["flavors"],
        quantity_options=options_data["quantities"],
        nudge_rules=options_data["nudges"],
        data_source="mock_fallback",
    )

    serialized = response.model_dump(mode="json")
    assert serialized["kid_session_id"] == str(session_id)
    assert serialized["level"] == 1
    assert serialized["wallet_balance_cents"] == 5000
    assert len(serialized["flavor_options"]) == 3
    assert len(serialized["quantity_options"]) == 3


def test_decision_request_validation():
    """Verify Screen5DecisionRequest validates unique flavors and valid payload."""
    session_id = uuid4()

    valid_req = Screen5DecisionRequest(
        kid_session_id=session_id,
        selected_flavors=["flavor_cherry", "flavor_lemon"],
        batch_quantity=40,
        nudge_fired_id="nudge_l1_single_flavor",
    )
    assert len(valid_req.selected_flavors) == 2
    assert valid_req.batch_quantity == 40

    # Duplicate flavors must fail validation
    with pytest.raises(ValidationError):
        Screen5DecisionRequest(
            kid_session_id=session_id,
            selected_flavors=["flavor_cherry", "flavor_cherry"],
            batch_quantity=40,
        )

    # Empty flavors must fail validation
    with pytest.raises(ValidationError):
        Screen5DecisionRequest(
            kid_session_id=session_id,
            selected_flavors=[],
            batch_quantity=40,
        )


def test_decision_response_structure():
    """Verify Screen5DecisionResponse matches the defined contract."""
    session_id = uuid4()
    decision_id = uuid4()

    persisted = Screen5PersistedPayload(
        selected_flavors=["flavor_cherry", "flavor_lemon"],
        flavor_count=2,
        batch_quantity=40,
        nudge_fired_id="nudge_l1_single_flavor",
    )

    response = Screen5DecisionResponse(
        status="success",
        decision_id=decision_id,
        kid_session_id=session_id,
        screen_id="screen_5",
        persisted_payload=persisted,
        next_screen="screen_6",
    )

    data = response.model_dump(mode="json")
    assert data["status"] == "success"
    assert data["screen_id"] == "screen_5"
    assert data["next_screen"] == "screen_6"
    assert data["persisted_payload"]["flavor_count"] == 2
