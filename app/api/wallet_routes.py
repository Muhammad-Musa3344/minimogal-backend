from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.supabase_client import supabase
from app.middleware.auth import require_auth

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

class FundWalletRequest(BaseModel):
    child_name: str
    child_age: int
    wallet_amount_dollars: int

@router.post("/fund")
def fund_wallet(payload: FundWalletRequest, account_id: str = Depends(require_auth)):
    if not (25 <= payload.wallet_amount_dollars <= 100):
        raise HTTPException(status_code=400, detail="Wallet amount must be $25-$100")
    if not (7 <= payload.child_age <= 14):
        raise HTTPException(status_code=400, detail="Age must be 7-14")

    default_level = 1 if payload.child_age <= 8 else 2

    result = supabase.table("child_profiles").insert({
        "account_id": account_id,
        "name": payload.child_name,
        "age": payload.child_age,
        "default_level": default_level,
        "wallet_balance_cents": payload.wallet_amount_dollars * 100,
    }).execute()

    return {"child_id": result.data[0]["id"], "wallet_balance_cents": payload.wallet_amount_dollars * 100}

@router.get("/{child_id}")
def get_wallet(child_id: str, account_id: str = Depends(require_auth)):
    result = (
        supabase.table("child_profiles")
        .select("id, name, age, wallet_balance_cents")
        .eq("id", child_id)
        .eq("account_id", account_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Child profile not found")
    return result.data