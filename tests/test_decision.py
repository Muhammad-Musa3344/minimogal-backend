from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.db.supabase_client import supabase
import uuid

@pytest.fixture
def create_kid_session():
    def kid_session():
        result = (
                supabase
                .table("households")
                .insert({
                    "email": f"test{uuid.uuid4()}@email.com",
                    "auth_provider":"email"
                })
                .execute())
        household_id =  result.data[0]["id"]
        result = (
            supabase
            .table("kid_session")
            .insert({
                "household_id": household_id
            })
            .execute()
        )
        kid_session_id = result.data[0]["id"]
        return kid_session_id 
    return kid_session

client = TestClient(app)

def test_set_decision(create_kid_session):
    payload = {
        "kid_session_id": create_kid_session(),
        "decision_key": "test",
        "decision_value":"test",
        "value_jsonb": {
            "style": "visual",
            "confidence": 0.85
        },
        "source_screen": "screen-5"
    }
    response =  client.post("/api/decisions/set-decision", json=payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_set_decision_updates_existing_decision(create_kid_session):
    kid_session_id = create_kid_session()

    first_payload = {
        "kid_session_id": kid_session_id,
        "decision_key": "QUANTITY_FLAVOR",
        "decision_value": "QTY_10",
        "value_jsonb": {
            "quantity": 10
        },
        "source_screen": "screen-5"
    }

    second_payload = {
        "kid_session_id": kid_session_id,
        "decision_key": "QUANTITY_FLAVOR",
        "decision_value": "QTY_20",
        "value_jsonb": {
            "quantity": 20
        },
        "source_screen": "screen-6"
    }

    response = client.post("/api/decisions/set-decision", json = first_payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}
     
    response = client.post("/api/decisions/set-decision", json = second_payload) 
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_set_decision_list(create_kid_session):
    kid_session_id= create_kid_session()
    payload = {
        "decisions": [
    {
        "kid_session_id": create_kid_session(),
        "decision_key": "PARTNER",
        "decision_value": "QTY_10",
        "value_jsonb": {
            "quantity": 10
        },
        "source_screen": "screen-5"
    },
            {
        "kid_session_id": kid_session_id,
        "decision_key": "ADVERTISING",
        "decision_value": "QTY_10",
        "value_jsonb": {
            "quantity": 10
        },
        "source_screen": "screen-5"
    },
    {
        "kid_session_id": create_kid_session(),
        "decision_key": "LOCATION",
        "decision_value": "QTY_10",
        "value_jsonb": {
            "quantity": 10
        },
        "source_screen": "screen-5"
    },
    {
        "kid_session_id": create_kid_session(),
        "decision_key": "PRICE",
        "decision_value": "QTY_10",
        "value_jsonb": {
            "quantity": 10
        },
        "source_screen": "screen-5"
    },
    {
        "kid_session_id": kid_session_id,
        "decision_key": "DURATION",
        "decision_value": "QTY_10",
        "value_jsonb": {
            "quantity": 10
        },
        "source_screen": "screen-8"
    }
    ]}


    response = client.post("/api/decisions/set-all-decisions", json = payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}
    

def test_get_all_decisions():
    kid_session_id = "040c7874-ff1c-43f0-a7f2-012236e7fe3b"
    response = client.get(f"/api/decisions/get-all-decisions/{kid_session_id}")
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_get_decision():
    kid_session_id = "040c7874-ff1c-43f0-a7f2-012236e7fe3b"
    decision_key = 'QUANTITY_FLAVOR'
    response = client.get(f"/api/decisions/get-decision/{kid_session_id}/{decision_key}")
    assert response.status_code == 200
    assert response.json()["success"] == True

