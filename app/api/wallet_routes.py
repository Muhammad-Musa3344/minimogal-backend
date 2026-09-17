# app/api/wallet_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from app.db.supabase_client import supabase
from app.middleware.auth import require_auth
from app.services.wallet_service import (
    WalletService,
    InsufficientBalanceError,
    InvalidAmountError,
    WalletError,
)

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


class FundWalletRequest(BaseModel):
    child_name: str
    child_age: int
    wallet_amount_dollars: int


class DeductWalletRequest(BaseModel):
    kid_session_id: str
    amount_cents: int = Field(..., gt=0, description="Deduction amount in cents")
    reason: str = Field(..., description="Reason for deduction, e.g. 'ingredient_purchase'")
    screen_id: Optional[str] = Field(None, description="Screen triggering deduction, e.g. 'screen_6_prep'")


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

    if not kid_result.data:
        raise HTTPException(status_code=400, detail="Failed to create kid session")

    kid_session_id = kid_result.data[0]["id"]
    funding_cents = payload.wallet_amount_dollars * 100

    # Fund via WalletService (append-only transaction in wallet_ledger)
    try:
        tx = WalletService.fund(
            kid_session_id=kid_session_id,
            amount_cents=funding_cents,
            reason="initial_fund",
            screen_id="screen_2_fund_wallet",
        )
    except WalletError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "child_id": kid_session_id,
        "wallet_balance_cents": tx.new_balance_cents,
        "transaction_id": tx.transaction_id,
    }


@router.post("/deduct")
def deduct_wallet(payload: DeductWalletRequest, account_id: str = Depends(require_auth)):
    # Verify session ownership
    kid = (
        supabase.table("kid_session")
        .select("id")
        .eq("id", payload.kid_session_id)
        .eq("household_id", account_id)
        .maybe_single()
        .execute()
    )
    if not kid.data:
        raise HTTPException(status_code=404, detail="Kid session not found")

    try:
        tx = WalletService.deduct(
            kid_session_id=payload.kid_session_id,
            amount_cents=payload.amount_cents,
            reason=payload.reason,
            screen_id=payload.screen_id,
        )
        return tx.model_dump()
    except InsufficientBalanceError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "insufficient_funds",
                "message": str(e),
                "current_balance_cents": e.current_balance_cents,
                "requested_deduct_cents": e.requested_deduct_cents,
            },
        )
    except InvalidAmountError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except WalletError as e:
        raise HTTPException(status_code=500, detail=str(e))


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

    balance = WalletService.get_balance(kid_session_id)
    return {**kid.data, "wallet_balance_cents": balance}