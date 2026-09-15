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

    # Create the kid_session
    kid_result = supabase.table("kid_session").insert({
        "household_id": account_id,
        "name": payload.child_name,
        "age": payload.child_age,
    }).execute()

    kid_session_id = kid_result.data[0]["id"]

    # Fund via wallet_ledger (append-only transaction)
    supabase.table("wallet_ledger").insert({
        "kid_session_id": kid_session_id,
        "amount_cents": payload.wallet_amount_dollars * 100,
        "reason": "initial_fund",
        "screen_id": "screen_2_fund_wallet",
    }).execute()

    return {"child_id": kid_session_id, "wallet_balance_cents": payload.wallet_amount_dollars * 100}


@router.get("/{kid_session_id}")
def get_wallet(kid_session_id: str, account_id: str = Depends(require_auth)):
    kid = (
        supabase.table("kid_session")
        .select("id, name, age")
        .eq("id", kid_session_id)
        .eq("household_id", account_id)
        .maybe_single()
        .execute()
    )
    if not kid.data:
        raise HTTPException(status_code=404, detail="Kid session not found")

    ledger = (
        supabase.table("wallet_ledger")
        .select("amount_cents")
        .eq("kid_session_id", kid_session_id)
        .execute()
    )
    balance = sum(row["amount_cents"] for row in ledger.data)

    return {**kid.data, "wallet_balance_cents": balance}