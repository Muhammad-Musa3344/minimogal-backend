# tests/test_wallet_service.py
"""
Unit tests for WalletService (MOGUL-9 / MOGUL-10)

Validates:
1. Initial funding: Inserts positive transaction, calculates correct balance.
2. Sequential deductions: Decrements balance via append-only negative transactions.
3. Insufficient balance rejection: Throws InsufficientBalanceError without appending bad row.
4. Idempotency: Re-calling deduct with same screen_id & reason does not double deduct.
5. Invalid amount validation: Rejects zero and negative amounts.
6. Audit log integrity: get_history returns all ledger transactions chronologically.
7. Concurrent deduction safety.
"""

import pytest
import threading
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.services.wallet_service import (
    WalletService,
    InsufficientBalanceError,
    InvalidAmountError,
    WalletTransactionResult,
)


class MockSupabaseDB:
    """In-memory mock for Supabase table operations on wallet_ledger and kid_session."""

    def __init__(self):
        self.wallet_ledger = []
        self._lock = threading.Lock()

    def table(self, name: str):
        if name == "wallet_ledger":
            return MockTableQuery(self)
        raise ValueError(f"Unknown mock table: {name}")


class MockTableQuery:
    def __init__(self, db: MockSupabaseDB):
        self.db = db
        self._filters = []
        self._order_by = None
        self._insert_data = None

    def select(self, columns: str):
        return self

    def eq(self, column: str, value):
        self._filters.append((column, value))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_by = (column, desc)
        return self

    def insert(self, data: dict):
        self._insert_data = data
        return self

    def execute(self):
        with self.db._lock:
            if self._insert_data is not None:
                new_row = {
                    "id": str(uuid4()),
                    "kid_session_id": str(self._insert_data["kid_session_id"]),
                    "amount_cents": int(self._insert_data["amount_cents"]),
                    "reason": str(self._insert_data["reason"]),
                    "screen_id": self._insert_data.get("screen_id"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                self.db.wallet_ledger.append(new_row)
                res = MagicMock()
                res.data = [new_row]
                return res

            # Select with filters
            matched = []
            for row in self.db.wallet_ledger:
                match = True
                for col, val in self._filters:
                    if row.get(col) != val:
                        match = False
                        break
                if match:
                    matched.append(row)

            if self._order_by:
                col, desc = self._order_by
                matched.sort(key=lambda r: r.get(col, ""), reverse=desc)

            res = MagicMock()
            res.data = matched
            return res


@pytest.fixture
def mock_db():
    return MockSupabaseDB()


def test_initial_fund(mock_db):
    """Test initial funding of a kid's wallet."""
    kid_id = uuid4()
    
    # Balance should start at 0
    assert WalletService.get_balance(kid_id, client=mock_db) == 0

    # Fund with $50.00 (5000 cents)
    tx = WalletService.fund(
        kid_session_id=kid_id,
        amount_cents=5000,
        reason="initial_fund",
        screen_id="screen_2_fund_wallet",
        client=mock_db,
    )

    assert tx.amount_cents == 5000
    assert tx.new_balance_cents == 5000
    assert tx.is_idempotent_replay is False
    assert WalletService.get_balance(kid_id, client=mock_db) == 5000


def test_sequential_deductions(mock_db):
    """Test multiple sequential deductions across screens 6, 7, and 9."""
    kid_id = uuid4()

    # Initial Fund: $50.00
    WalletService.fund(kid_id, 5000, client=mock_db)

    # Screen 6: Ingredient purchase ($15.00)
    tx1 = WalletService.deduct(
        kid_session_id=kid_id,
        amount_cents=1500,
        reason="ingredient_purchase",
        screen_id="screen_6_prep_level",
        client=mock_db,
    )
    assert tx1.new_balance_cents == 3500
    assert WalletService.get_balance(kid_id, client=mock_db) == 3500

    # Screen 7: Stand fee ($5.00)
    tx2 = WalletService.deduct(
        kid_session_id=kid_id,
        amount_cents=500,
        reason="stand_fee",
        screen_id="screen_7_location",
        client=mock_db,
    )
    assert tx2.new_balance_cents == 3000
    assert WalletService.get_balance(kid_id, client=mock_db) == 3000

    # Screen 9: Sign purchase ($10.00)
    tx3 = WalletService.deduct(
        kid_session_id=kid_id,
        amount_cents=1000,
        reason="sign_cost",
        screen_id="screen_9_pricing",
        client=mock_db,
    )
    assert tx3.new_balance_cents == 2000
    assert WalletService.get_balance(kid_id, client=mock_db) == 2000


def test_insufficient_balance_rejection(mock_db):
    """Test that attempting to overdraw the wallet raises InsufficientBalanceError."""
    kid_id = uuid4()

    # Initial Fund: $25.00 (2500 cents)
    WalletService.fund(kid_id, 2500, client=mock_db)

    # Attempt to deduct $30.00 (3000 cents)
    with pytest.raises(InsufficientBalanceError) as exc_info:
        WalletService.deduct(
            kid_session_id=kid_id,
            amount_cents=3000,
            reason="expensive_ingredients",
            screen_id="screen_6_prep_level",
            client=mock_db,
        )

    assert exc_info.value.current_balance_cents == 2500
    assert exc_info.value.requested_deduct_cents == 3000

    # Balance must remain unchanged ($25.00)
    assert WalletService.get_balance(kid_id, client=mock_db) == 2500
    # Ledger should contain ONLY the 1 initial funding row
    assert len(mock_db.wallet_ledger) == 1


def test_idempotent_deductions(mock_db):
    """Test that repeating the same deduction does not double charge."""
    kid_id = uuid4()

    # Initial Fund: $50.00
    WalletService.fund(kid_id, 5000, client=mock_db)

    # First deduction call from Screen 6
    tx1 = WalletService.deduct(
        kid_session_id=kid_id,
        amount_cents=1200,
        reason="ingredient_purchase",
        screen_id="screen_6_prep_level",
        client=mock_db,
    )
    assert tx1.is_idempotent_replay is False
    assert tx1.new_balance_cents == 3800

    # Second identical deduction call (e.g. user refreshed or double clicked)
    tx2 = WalletService.deduct(
        kid_session_id=kid_id,
        amount_cents=1200,
        reason="ingredient_purchase",
        screen_id="screen_6_prep_level",
        client=mock_db,
    )
    assert tx2.is_idempotent_replay is True
    assert tx2.transaction_id == tx1.transaction_id
    assert tx2.new_balance_cents == 3800

    # Balance must still be 3800 cents, NOT 2600 cents
    assert WalletService.get_balance(kid_id, client=mock_db) == 3800
    # Ledger must contain exactly 2 rows (1 fund + 1 deduct)
    assert len(mock_db.wallet_ledger) == 2


def test_invalid_amounts(mock_db):
    """Test zero and negative amounts throw InvalidAmountError."""
    kid_id = uuid4()

    with pytest.raises(InvalidAmountError):
        WalletService.fund(kid_id, 0, client=mock_db)

    with pytest.raises(InvalidAmountError):
        WalletService.fund(kid_id, -500, client=mock_db)

    with pytest.raises(InvalidAmountError):
        WalletService.deduct(kid_id, 0, reason="test", client=mock_db)

    with pytest.raises(InvalidAmountError):
        WalletService.deduct(kid_id, -1000, reason="test", client=mock_db)


def test_ledger_history_audit(mock_db):
    """Test full chronological audit trail retrieved via get_history."""
    kid_id = uuid4()

    WalletService.fund(kid_id, 5000, reason="initial_fund", screen_id="screen_2", client=mock_db)
    WalletService.deduct(kid_id, 1000, reason="ingredients", screen_id="screen_6", client=mock_db)
    WalletService.deduct(kid_id, 500, reason="stand", screen_id="screen_7", client=mock_db)

    history = WalletService.get_history(kid_id, client=mock_db)
    assert len(history) == 3

    assert history[0].amount_cents == 5000
    assert history[0].reason == "initial_fund"
    assert history[1].amount_cents == -1000
    assert history[1].reason == "ingredients"
    assert history[2].amount_cents == -500
    assert history[2].reason == "stand"


def test_concurrent_deductions_simulation(mock_db):
    """Simulate multiple threads attempting deductions to test race conditions."""
    kid_id = uuid4()
    # Fund with exactly 1000 cents ($10.00)
    WalletService.fund(kid_id, 1000, client=mock_db)

    success_count = 0
    failure_count = 0
    lock = threading.Lock()

    def try_deduct(amount, reason, screen_id):
        nonlocal success_count, failure_count
        try:
            WalletService.deduct(
                kid_session_id=kid_id,
                amount_cents=amount,
                reason=reason,
                screen_id=screen_id,
                client=mock_db,
            )
            with lock:
                success_count += 1
        except InsufficientBalanceError:
            with lock:
                failure_count += 1

    threads = [
        threading.Thread(target=try_deduct, args=(600, "purchase_a", "screen_6")),
        threading.Thread(target=try_deduct, args=(600, "purchase_b", "screen_7")),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # One deduction of 600 must succeed, the other 600 must fail (1000 < 1200)
    assert success_count == 1
    assert failure_count == 1
    assert WalletService.get_balance(kid_id, client=mock_db) == 400
