# tests/test_screen_5_routes.py
"""
Unit and Integration tests for Screen 5 Routes (MOGUL-12 / MOGUL-13 / MOGUL-14)
"""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.db.supabase_client import supabase


@pytest.fixture
def client():
    return TestClient(app)


def test_get_screen_5_options_level_1(client):
    """Test options retrieval for Level 1 kid (age 8)."""
    kid_id = str(uuid4())
    mock_kid = {"id": kid_id, "name": "Leo", "age": 8, "age_tier": "7-8"}

    with patch.object(supabase, "table") as mock_table:
        def table_side_effect(name):
            t = MagicMock()
            if name == "kid_session":
                t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=mock_kid)
            elif name == "wallet_ledger":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"amount_cents": 5000}])
            else:
                # Mock empty return for DS tables to test fallback
                t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=None)
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            return t
        
        mock_table.side_effect = table_side_effect

        response = client.get(f"/api/v1/screens/screen-5/options?kid_session_id={kid_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["kid_session_id"] == kid_id
        assert data["level"] == 1
        assert data["wallet_balance_cents"] == 5000
        assert data["max_flavors_allowed"] == 2
        assert len(data["flavor_options"]) >= 3
        assert len(data["quantity_options"]) == 3
        assert data["quantity_options"][0]["units"] == 20


def test_get_screen_5_options_level_2(client):
    """Test options retrieval for Level 2 kid (age 10)."""
    kid_id = str(uuid4())
    mock_kid = {"id": kid_id, "name": "Sam", "age": 10, "age_tier": "9-10"}

    with patch.object(supabase, "table") as mock_table:
        def table_side_effect(name):
            t = MagicMock()
            if name == "kid_session":
                t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=mock_kid)
            elif name == "wallet_ledger":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"amount_cents": 7500}])
            else:
                t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=None)
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            return t
        
        mock_table.side_effect = table_side_effect

        response = client.get(f"/api/v1/screens/screen-5/options?kid_session_id={kid_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 2
        assert data["wallet_balance_cents"] == 7500
        assert data["quantity_options"][0]["units"] == 25


def test_submit_screen_5_decision_success(client):
    """Test valid inventory decision submission persisting to decision_log."""
    kid_id = str(uuid4())
    decision_id = str(uuid4())
    mock_kid = {"id": kid_id, "name": "Leo", "age": 8, "age_tier": "7-8"}

    with patch.object(supabase, "table") as mock_table:
        def table_side_effect(name):
            t = MagicMock()
            if name == "kid_session":
                t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=mock_kid)
            elif name == "decision_log":
                t.insert.return_value.execute.return_value = MagicMock(data=[{"id": decision_id}])
            return t
        
        mock_table.side_effect = table_side_effect

        response = client.post(
            "/api/v1/screens/screen-5/decisions",
            json={
                "kid_session_id": kid_id,
                "selected_flavors": ["flavor_cherry", "flavor_blue_raspberry"],
                "batch_quantity": 40,
                "nudge_fired_id": "nudge_l1_single_flavor",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["decision_id"] == decision_id
        assert data["screen_id"] == "screen_5"
        assert data["next_screen"] == "screen_6"
        assert data["persisted_payload"]["flavor_count"] == 2
        assert data["persisted_payload"]["batch_quantity"] == 40


def test_submit_screen_5_decision_duplicate_flavors(client):
    """Test that duplicate flavors are rejected with 422."""
    kid_id = str(uuid4())

    response = client.post(
        "/api/v1/screens/screen-5/decisions",
        json={
            "kid_session_id": kid_id,
            "selected_flavors": ["flavor_cherry", "flavor_cherry"],
            "batch_quantity": 40,
        },
    )
    assert response.status_code == 422


def test_submit_screen_5_decision_exceeded_flavors(client):
    """Test that selecting more flavors than allowed for level is rejected with 400."""
    kid_id = str(uuid4())
    mock_kid = {"id": kid_id, "name": "Leo", "age": 8, "age_tier": "7-8"}  # Level 1 max 2 flavors

    with patch.object(supabase, "table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=mock_kid)

        response = client.post(
            "/api/v1/screens/screen-5/decisions",
            json={
                "kid_session_id": kid_id,
                "selected_flavors": ["flavor_cherry", "flavor_blue_raspberry", "flavor_lemon"],
                "batch_quantity": 40,
            },
        )
        assert response.status_code == 400
        assert "Exceeded max allowed flavors" in response.json()["detail"]


def test_submit_screen_5_decision_invalid_quantity(client):
    """Test that an invalid batch quantity is rejected with 400."""
    kid_id = str(uuid4())
    mock_kid = {"id": kid_id, "name": "Leo", "age": 8, "age_tier": "7-8"}

    with patch.object(supabase, "table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=mock_kid)

        response = client.post(
            "/api/v1/screens/screen-5/decisions",
            json={
                "kid_session_id": kid_id,
                "selected_flavors": ["flavor_cherry"],
                "batch_quantity": 99,  # Invalid for Level 1 [20, 40, 60]
            },
        )
        assert response.status_code == 400
        assert "Invalid batch quantity" in response.json()["detail"]


def test_get_screen_5_decision_state_found(client):
    """Test retrieving previously persisted decision for Screen 5."""
    kid_id = str(uuid4())
    decision_id = str(uuid4())
    mock_row = {
        "id": decision_id,
        "value_jsonb": {
            "selected_flavors": ["flavor_cherry", "flavor_lemon"],
            "flavor_count": 2,
            "batch_quantity": 40,
            "nudge_fired_id": None,
        },
        "created_at": "2026-09-19T01:00:00Z",
    }

    with patch.object(supabase, "table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[mock_row])

        response = client.get(f"/api/v1/screens/screen-5/decisions/{kid_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["has_decision"] is True
        assert data["decision_id"] == decision_id
        assert data["persisted_payload"]["batch_quantity"] == 40


def test_get_screen_5_decision_state_empty(client):
    """Test retrieving decision state when no decision has been made yet."""
    kid_id = str(uuid4())

    with patch.object(supabase, "table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

        response = client.get(f"/api/v1/screens/screen-5/decisions/{kid_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["has_decision"] is False
        assert data["decision_id"] is None
        assert data["persisted_payload"] is None
