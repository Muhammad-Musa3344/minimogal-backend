from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.supabase_client import supabase

router = APIRouter(prefix="/api/auth", tags=["auth"])

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(payload: SignupRequest):
    result = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
    if result.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")
    supabase.table("accounts").insert({
        "id": result.user.id,
        "email": payload.email,
        "auth_provider": "email",
        "email_verified": False,
    }).execute()
    return {"user_id": result.user.id, "email_verification_sent": True}

@router.post("/signin")
def signin(payload: SigninRequest):
    result = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
    if result.session is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": result.session.access_token, "user_id": result.user.id}