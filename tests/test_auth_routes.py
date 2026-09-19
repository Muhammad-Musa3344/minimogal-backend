# tests/test_auth_routes.py
"""
Unit tests for MOGUL-6 / MOGUL-7 Auth Routes (Google OAuth, Magic Link, Screen 2 Onboarding)
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


def test_signup_flow(client):
    """Test parent email/password signup on Screen 2."""
    test_uid = str(uuid4())
    mock_user = MagicMock()
    mock_user.id = test_uid
    mock_user.email = "parent@example.com"
    mock_user.email_confirmed_at = None

    mock_signup_res = MagicMock()
    mock_signup_res.user = mock_user

    with patch.object(supabase.auth, "sign_up", return_value=mock_signup_res):
        with patch.object(supabase, "table") as mock_table:
            mock_table.return_value.upsert.return_value.execute.return_value = MagicMock()
            
            response = client.post(
                "/api/auth/signup",
                json={
                    "name": "Jane Doe",
                    "email": "parent@example.com",
                    "password": "Password123!",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_uid
            assert data["email_verification_sent"] is True


def test_signin_flow(client):
    """Test parent signin returning session access token."""
    test_uid = str(uuid4())
    mock_user = MagicMock()
    mock_user.id = test_uid

    mock_session = MagicMock()
    mock_session.access_token = "mock-jwt-token-12345"

    mock_signin_res = MagicMock()
    mock_signin_res.user = mock_user
    mock_signin_res.session = mock_session

    with patch.object(supabase.auth, "sign_in_with_password", return_value=mock_signin_res):
        response = client.post(
            "/api/auth/signin",
            json={
                "email": "parent@example.com",
                "password": "Password123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "mock-jwt-token-12345"
        assert data["user_id"] == test_uid
        assert data["token_type"] == "bearer"


def test_magic_link_flow(client):
    """Test magic link passwordless OTP dispatch."""
    mock_otp_res = MagicMock()

    with patch.object(supabase.auth, "sign_in_with_otp", return_value=mock_otp_res):
        response = client.post(
            "/api/auth/magic-link",
            json={"email": "magicparent@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["email"] == "magicparent@example.com"


def test_verify_otp_flow(client):
    """Test verifying magic link / OTP code and receiving session token."""
    test_uid = str(uuid4())
    mock_user = MagicMock()
    mock_user.id = test_uid

    mock_session = MagicMock()
    mock_session.access_token = "mock-otp-jwt-token-67890"

    mock_verify_res = MagicMock()
    mock_verify_res.user = mock_user
    mock_verify_res.session = mock_session

    with patch.object(supabase.auth, "verify_otp", return_value=mock_verify_res):
        with patch.object(supabase, "table") as mock_table:
            mock_table.return_value.upsert.return_value.execute.return_value = MagicMock()

            response = client.post(
                "/api/auth/verify-otp",
                json={
                    "email": "magicparent@example.com",
                    "token": "123456",
                    "type": "email",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "mock-otp-jwt-token-67890"
            assert data["user_id"] == test_uid


def test_google_oauth_url(client):
    """Test generating Google OAuth authorization URL."""
    response = client.get("/api/auth/google/url")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "google"
    assert "url" in data
    assert "redirect_to" in data


def test_google_signin(client):
    """Test exchanging Google ID token for Supabase session token."""
    test_uid = str(uuid4())
    mock_user = MagicMock()
    mock_user.id = test_uid
    mock_user.email = "googleparent@gmail.com"

    mock_session = MagicMock()
    mock_session.access_token = "mock-google-jwt-token-abcde"

    mock_google_res = MagicMock()
    mock_google_res.user = mock_user
    mock_google_res.session = mock_session

    with patch.object(supabase.auth, "sign_in_with_id_token", return_value=mock_google_res):
        with patch.object(supabase, "table") as mock_table:
            mock_table.return_value.upsert.return_value.execute.return_value = MagicMock()

            response = client.post(
                "/api/auth/google",
                json={"id_token": "google-oauth-token-sample"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "mock-google-jwt-token-abcde"
            assert data["user_id"] == test_uid


def test_get_me_unauthorized(client):
    """Test that /api/auth/me rejects requests missing a Bearer token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 422 or response.status_code == 401


def test_get_me_authenticated(client):
    """Test /api/auth/me returns household and associated kid sessions."""
    test_uid = str(uuid4())
    
    mock_user_resp = MagicMock()
    mock_user = MagicMock()
    mock_user.id = test_uid
    mock_user_resp.user = mock_user

    mock_household = {
        "id": test_uid,
        "email": "parent@example.com",
        "auth_provider": "google",
        "email_verified": True,
        "created_at": "2026-09-19T00:00:00Z",
    }
    mock_kids = [
        {"id": str(uuid4()), "name": "Lily", "age": 8, "age_tier": "7-8"}
    ]

    with patch.object(supabase.auth, "get_user", return_value=mock_user_resp):
        with patch.object(supabase, "table") as mock_table:
            def table_side_effect(name):
                t = MagicMock()
                if name == "households":
                    t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=mock_household)
                elif name == "kid_session":
                    t.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(data=mock_kids)
                return t
            
            mock_table.side_effect = table_side_effect

            response = client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer mock-valid-jwt-token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["household"]["id"] == test_uid
            assert len(data["kid_sessions"]) == 1
            assert data["kid_sessions"][0]["name"] == "Lily"
