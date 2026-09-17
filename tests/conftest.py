from app.main import app

import pytest
import uuid
from fastapi.testclient import TestClient


from app.db.supabase_client import supabase







@pytest.fixture(scope="session")
def auth_headers():
    email=f"test{uuid.uuid4()}@mail.com"
    password = "TestPassword123"
    signup_result = supabase.auth.sign_up({
        "email": email,
        "password": password
    })

    login_result = supabase.auth.sign_in_with_password({
        "email": email,
        "password":password
    })
    access_token = login_result.session.access_token

    return {
        "access_token": access_token,
        "email": email
    }





@pytest.fixture(scope="session")
def auth_client(auth_headers):
    return TestClient(
        app,
        headers = {
            "Authorization": f"Bearer {auth_headers["access_token"]}"
        }
    )


@pytest.fixture
def create_kid_session(auth_headers):
    def kid_session():
        email = auth_headers["email"]
        result = (
                supabase
                .table("households")
                .select("id")
                .eq("email", email)
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



@pytest.fixture
def add_decision():
    def decision(kid_session_id):
        decision_key ='QUANTITY_FLAVOR'
        result = (supabase
                  .table("decision_log")
                  .insert({
                      "kid_session_id": kid_session_id,
                      "decision_key" : decision_key,
                       "decision_value": "QTY_20",
                       "value_jsonb": {},     
                        "source_screen": 1
                  })
                  .execute()
                  )

        return decision_key
    return decision

# tests/conftest.py
import os

# Set fallback environment variables for test execution
os.environ.setdefault("SUPABASE_URL", "https://mock-test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "mock-service-role-key-test")
os.environ.setdefault("SUPABASE_ANON_KEY", "mock-anon-key-test")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:5173")
