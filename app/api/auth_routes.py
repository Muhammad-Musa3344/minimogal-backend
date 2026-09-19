# app/api/auth_routes.py
"""
Authentication & Parent Onboarding (Screen 2) Routes — MOGUL-6 / MOGUL-7

Supports:
1. Email & Password: Standard signup and signin
2. Magic Link / Email OTP: Passwordless authentication via Supabase Auth
3. Google OAuth: ID Token verification & OAuth URL generation
4. Authenticated Session Info (/me): Retrieves parent household profile and registered kid sessions
"""

from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field

from app.db.supabase_client import supabase
from app.config import FRONTEND_ORIGIN
from app.middleware.auth import require_auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


# --- Request & Response Schemas ---

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Parent's full or display name")
    email: EmailStr = Field(..., description="Parent's email address")
    password: str = Field(..., min_length=6, description="Account password (min 6 chars)")


class SigninRequest(BaseModel):
    email: EmailStr = Field(..., description="Parent's email address")
    password: str = Field(..., description="Account password")


class MagicLinkRequest(BaseModel):
    email: EmailStr = Field(..., description="Parent's email address for passwordless login")


class VerifyOtpRequest(BaseModel):
    email: EmailStr = Field(..., description="Parent's email address")
    token: str = Field(..., description="6-digit OTP code or magic link token hash")
    type: str = Field("email", description="OTP type: 'email', 'magiclink', or 'signup'")


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Google ID Token returned by Google Sign-In SDK")


# --- Routes ---

@router.post("/signup")
def signup(payload: SignupRequest):
    """
    Creates a new parent account via email & password (Screen 2).
    A matching record in public.households is automatically created via database trigger.
    """
    try:
        result = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {"name": payload.name}
            }
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

    if result.user is None:
        raise HTTPException(status_code=400, detail="Signup failed: User could not be created")

    # Ensure households record is present (idempotent with DB trigger)
    try:
        supabase.table("households").upsert({
            "id": result.user.id,
            "email": payload.email,
            "auth_provider": "email",
            "email_verified": bool(result.user.email_confirmed_at),
        }).execute()
    except Exception:
        pass  # DB trigger handles creation

    return {
        "user_id": result.user.id,
        "email_verification_sent": not bool(result.user.email_confirmed_at),
        "message": "Account created successfully",
    }


@router.post("/signin")
def signin(payload: SigninRequest):
    """
    Signs in a parent using email & password.
    Returns access_token and user_id.
    """
    try:
        result = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")

    if result.session is None or result.user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "access_token": result.session.access_token,
        "user_id": result.user.id,
        "token_type": "bearer",
    }


@router.post("/magic-link")
def send_magic_link(payload: MagicLinkRequest):
    """
    Sends a passwordless Magic Link / OTP to the parent's email.
    """
    redirect_url = f"{FRONTEND_ORIGIN}/auth/callback"
    try:
        result = supabase.auth.sign_in_with_otp({
            "email": payload.email,
            "options": {
                "email_redirect_to": redirect_url,
                "should_create_user": True,
            }
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send magic link: {str(e)}")

    return {
        "success": True,
        "email": payload.email,
        "message": f"Magic link has been sent to {payload.email}",
    }


@router.post("/verify-otp")
def verify_otp(payload: VerifyOtpRequest):
    """
    Verifies an OTP code or magic link token.
    Returns a valid session access token and user_id.
    """
    try:
        result = supabase.auth.verify_otp({
            "email": payload.email,
            "token": payload.token,
            "type": payload.type,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or expired OTP: {str(e)}")

    if result.session is None or result.user is None:
        raise HTTPException(status_code=400, detail="OTP verification failed: no active session")

    # Ensure households record has email_verified: True
    try:
        supabase.table("households").upsert({
            "id": result.user.id,
            "email": payload.email,
            "auth_provider": "email",
            "email_verified": True,
        }).execute()
    except Exception:
        pass

    return {
        "access_token": result.session.access_token,
        "user_id": result.user.id,
        "token_type": "bearer",
    }


@router.get("/google/url")
def get_google_oauth_url():
    """
    Generates the Google OAuth sign-in URL redirecting to frontend callback.
    """
    redirect_url = f"{FRONTEND_ORIGIN}/auth/callback"
    try:
        result = supabase.auth.get_oauth_sign_in_url({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url,
                "query_params": {
                    "access_type": "offline",
                    "prompt": "consent",
                }
            }
        })
        return {
            "provider": "google",
            "url": result.url if hasattr(result, "url") else str(result),
            "redirect_to": redirect_url,
        }
    except Exception as e:
        # Fallback OAuth URL format for Supabase
        fallback_url = f"{supabase.supabase_url}/auth/v1/authorize?provider=google&redirect_to={redirect_url}"
        return {
            "provider": "google",
            "url": fallback_url,
            "redirect_to": redirect_url,
        }


@router.post("/google")
def google_signin(payload: GoogleAuthRequest):
    """
    Exchanges a Google ID Token for a Supabase session token.
    Ensures the parent household is recorded with auth_provider: 'google' and email_verified: true.
    """
    try:
        result = supabase.auth.sign_in_with_id_token({
            "provider": "google",
            "token": payload.id_token,
        })
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Google sign-in failed: {str(e)}")

    if result.session is None or result.user is None:
        raise HTTPException(status_code=401, detail="Google authentication failed")

    # Upsert household profile for Google provider
    try:
        supabase.table("households").upsert({
            "id": result.user.id,
            "email": result.user.email,
            "auth_provider": "google",
            "email_verified": True,
        }).execute()
    except Exception:
        pass

    return {
        "access_token": result.session.access_token,
        "user_id": result.user.id,
        "token_type": "bearer",
    }


@router.get("/me")
def get_current_user_profile(account_id: str = Depends(require_auth)):
    """
    Retrieves the authenticated parent's household profile and registered kid sessions.
    Protects data according to Row-Level Security.
    """
    household = (
        supabase.table("households")
        .select("id, email, auth_provider, email_verified, created_at")
        .eq("id", account_id)
        .maybe_single()
        .execute()
    )

    if not household.data:
        raise HTTPException(status_code=404, detail="Household profile not found")

    # Retrieve all kid sessions belonging to this household
    kid_sessions = (
        supabase.table("kid_session")
        .select("id, name, age, age_tier, avatar_config, created_at")
        .eq("household_id", account_id)
        .order("created_at", desc=False)
        .execute()
    )

    return {
        "household": household.data,
        "kid_sessions": kid_sessions.data if kid_sessions.data else [],
    }