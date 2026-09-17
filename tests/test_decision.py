from app.db.supabase_client import supabase
from .conftest import auth_client, create_kid_session, add_decision






def test_set_decision(create_kid_session, auth_client):
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
    response =  auth_client.post("/api/decisions/set-decision", json=payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_set_decision_updates_existing_decision(create_kid_session, auth_client):
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

    response = auth_client.post("/api/decisions/set-decision", json = first_payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}
     
    response = auth_client.post("/api/decisions/set-decision", json = second_payload) 
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_set_decision_list(create_kid_session, auth_client):
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


    response = auth_client.post("/api/decisions/set-all-decisions", json = payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}
    

def test_get_all_decisions(create_kid_session, auth_client):
    kid_session_id = create_kid_session()
    response = auth_client.get(f"/api/decisions/get-all-decisions/{kid_session_id}")
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_get_decision(create_kid_session, add_decision, auth_client):
    kid_session_id = create_kid_session()
    decision_key = add_decision(kid_session_id)
    response = auth_client.get(f"/api/decisions/get-decision/{kid_session_id}/{decision_key}")
    assert response.status_code == 200
    assert response.json()["success"] == True

