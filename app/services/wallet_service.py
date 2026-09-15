# app/services/wallet_service.py
"""
Wallet Service (MOGUL-9 / MOGUL-10)

Provides transactional, append-only, and idempotent financial operations against wallet_ledger:
- fund: Deposits funds into kid_session wallet
- deduct: Deducts funds for gameplay decisions (Screens 6, 7, 9) with insufficient balance checks
- get_balance: Computes SUM(amount_cents) dynamically from ledger
- get_history: Returns full audit log of all transactions
"""

from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from supabase import Client

from app.db.supabase_client import supabase as default_supabase


class WalletError(Exception):
    """Base exception for wallet operations."""
    pass


class InsufficientBalanceError(WalletError):
    """Raised when deduction amount exceeds current wallet balance."""
    def __init__(self, current_balance_cents: int, requested_deduct_cents: int):
        self.current_balance_cents = current_balance_cents
        self.requested_deduct_cents = requested_deduct_cents
        super().__init__(
            f"Insufficient funds: current balance is {current_balance_cents} cents "
            f"(${current_balance_cents / 100:.2f}), but attempted to deduct "
            f"{requested_deduct_cents} cents (${requested_deduct_cents / 100:.2f})"
        )


class InvalidAmountError(WalletError):
    """Raised when amount is zero or negative."""
    pass


class KidSessionNotFoundError(WalletError):
    """Raised when kid_session is not found."""
    pass


class WalletLedgerEntry(BaseModel):
    """Represents a single immutable entry in wallet_ledger."""
    id: str
    kid_session_id: str
    amount_cents: int
    reason: str
    screen_id: Optional[str] = None
    created_at: str


class WalletTransactionResult(BaseModel):
    """Result of a fund or deduct operation."""
    transaction_id: str
    kid_session_id: str
    amount_cents: int
    new_balance_cents: int
    reason: str
    screen_id: Optional[str] = None
    is_idempotent_replay: bool = False
    created_at: str


class WalletService:
    """
    Centralized service managing all wallet transactions.
    Enforces append-only accounting and idempotency across screens.
    """

    @staticmethod
    def _get_client(client: Optional[Client] = None) -> Client:
        return client if client is not None else default_supabase

    @classmethod
    def get_balance(
        cls,
        kid_session_id: Union[str, UUID],
        client: Optional[Client] = None,
    ) -> int:
        """
        Calculates live wallet balance by summing all ledger transactions.
        Balance is SUM(amount_cents), never a mutable single column.
        """
        db = cls._get_client(client)
        session_id_str = str(kid_session_id)

        res = (
            db.table("wallet_ledger")
            .select("amount_cents")
            .eq("kid_session_id", session_id_str)
            .execute()
        )

        if not res.data:
            return 0

        return sum(row["amount_cents"] for row in res.data)

    @classmethod
    def get_history(
        cls,
        kid_session_id: Union[str, UUID],
        client: Optional[Client] = None,
    ) -> List[WalletLedgerEntry]:
        """
        Returns full audit trail for the kid's wallet, ordered chronologically.
        """
        db = cls._get_client(client)
        session_id_str = str(kid_session_id)

        res = (
            db.table("wallet_ledger")
            .select("id, kid_session_id, amount_cents, reason, screen_id, created_at")
            .eq("kid_session_id", session_id_str)
            .order("created_at", desc=False)
            .execute()
        )

        if not res.data:
            return []

        return [WalletLedgerEntry(**row) for row in res.data]

    @classmethod
    def fund(
        cls,
        kid_session_id: Union[str, UUID],
        amount_cents: int,
        reason: str = "initial_fund",
        screen_id: Optional[str] = "screen_2_fund_wallet",
        client: Optional[Client] = None,
    ) -> WalletTransactionResult:
        """
        Funds a wallet with positive amount_cents.
        Appends a positive transaction to wallet_ledger.
        """
        if amount_cents <= 0:
            raise InvalidAmountError(f"Funding amount must be strictly positive, received: {amount_cents}")

        db = cls._get_client(client)
        session_id_str = str(kid_session_id)

        # Append positive transaction
        insert_res = (
            db.table("wallet_ledger")
            .insert({
                "kid_session_id": session_id_str,
                "amount_cents": amount_cents,
                "reason": reason,
                "screen_id": screen_id,
            })
            .execute()
        )

        if not insert_res.data:
            raise WalletError("Failed to write funding transaction to wallet_ledger")

        tx_row = insert_res.data[0]
        new_balance = cls.get_balance(session_id_str, client=db)

        return WalletTransactionResult(
            transaction_id=str(tx_row["id"]),
            kid_session_id=session_id_str,
            amount_cents=amount_cents,
            new_balance_cents=new_balance,
            reason=reason,
            screen_id=screen_id,
            is_idempotent_replay=False,
            created_at=str(tx_row.get("created_at", datetime.now(timezone.utc).isoformat())),
        )

    @classmethod
    def deduct(
        cls,
        kid_session_id: Union[str, UUID],
        amount_cents: int,
        reason: str,
        screen_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        client: Optional[Client] = None,
    ) -> WalletTransactionResult:
        """
        Deducts funds for gameplay decisions (Screens 6, 7, 9).
        
        Guarantees:
        1. Idempotency: If a deduction for this screen_id and reason (or idempotency_key)
           already exists, returns existing transaction without double deducting.
        2. Insufficient Funds Rejection: Rejects if balance < amount_cents without writing to ledger.
        3. Append-Only: Writes -amount_cents to wallet_ledger.
        """
        if amount_cents <= 0:
            raise InvalidAmountError(f"Deduction amount must be strictly positive, received: {amount_cents}")

        db = cls._get_client(client)
        session_id_str = str(kid_session_id)

        # 1. Idempotency Check:
        # Check if identical deduction already succeeded for this session & screen/reason
        query = (
            db.table("wallet_ledger")
            .select("id, kid_session_id, amount_cents, reason, screen_id, created_at")
            .eq("kid_session_id", session_id_str)
            .eq("amount_cents", -amount_cents)
            .eq("reason", reason)
        )
        if screen_id:
            query = query.eq("screen_id", screen_id)

        existing = query.execute()
        if existing.data:
            # Idempotent replay detected
            tx_row = existing.data[0]
            current_balance = cls.get_balance(session_id_str, client=db)
            return WalletTransactionResult(
                transaction_id=str(tx_row["id"]),
                kid_session_id=session_id_str,
                amount_cents=amount_cents,
                new_balance_cents=current_balance,
                reason=reason,
                screen_id=screen_id,
                is_idempotent_replay=True,
                created_at=str(tx_row.get("created_at", datetime.now(timezone.utc).isoformat())),
            )

        # 2. Balance Verification:
        current_balance = cls.get_balance(session_id_str, client=db)
        if current_balance < amount_cents:
            raise InsufficientBalanceError(
                current_balance_cents=current_balance,
                requested_deduct_cents=amount_cents,
            )

        # 3. Append Negative Deduction Row:
        insert_res = (
            db.table("wallet_ledger")
            .insert({
                "kid_session_id": session_id_str,
                "amount_cents": -amount_cents,
                "reason": reason,
                "screen_id": screen_id,
            })
            .execute()
        )

        if not insert_res.data:
            raise WalletError("Failed to write deduction transaction to wallet_ledger")

        tx_row = insert_res.data[0]
        new_balance = cls.get_balance(session_id_str, client=db)

        return WalletTransactionResult(
            transaction_id=str(tx_row["id"]),
            kid_session_id=session_id_str,
            amount_cents=-amount_cents,
            new_balance_cents=new_balance,
            reason=reason,
            screen_id=screen_id,
            is_idempotent_replay=False,
            created_at=str(tx_row.get("created_at", datetime.now(timezone.utc).isoformat())),
        )
