# app/api/screen_5_routes.py
"""
Screen 5: Flavor & Quantity Selection Routes (MOGUL-12 / MOGUL-13 / MOGUL-14)

Provides:
1. GET /api/v1/screens/screen-5/options: Level-gated flavor catalog, batch size options,
   AI nudge rules, and read-only wallet balance.
2. POST /api/v1/screens/screen-5/decisions: Validates choices against level constraints,
   writes decision to decision_log, and routes to Screen 6 (Prep Level).
3. GET /api/v1/screens/screen-5/decisions/{kid_session_id}: Retrieves existing decision state.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends

from app.db.supabase_client import supabase
from app.services.wallet_service import WalletService
from app.schemas.screen_5 import (
    Screen5OptionsResponse,
    Screen5DecisionRequest,
    Screen5DecisionResponse,
    Screen5PersistedPayload,
    Screen5DecisionStateResponse,
    FlavorOption,
    QuantityOption,
    NudgeRule,
    MockFlavorQuantityProvider,
)

router = APIRouter(prefix="/api/v1/screens/screen-5", tags=["screen-5"])


def resolve_session_level(kid_session_id: str) -> Dict[str, Any]:
    """Fetches kid_session and resolves the gameplay level (1, 2, or 3)."""
    res = (
        supabase.table("kid_session")
        .select("id, name, age, age_tier")
        .eq("id", str(kid_session_id))
        .maybe_single()
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Kid session not found")

    kid = res.data
    age = kid.get("age", 8)
    age_tier = kid.get("age_tier")

    if age_tier == "7-8" or (age and age <= 8):
        level = 1
    elif age_tier == "9-10" or (age and 9 <= age <= 10):
        level = 2
    else:
        level = 3

    return {"kid": kid, "level": level}


@router.get("/options", response_model=Screen5OptionsResponse)
def get_screen_5_options(kid_session_id: str = Query(..., description="Active player session ID")):
    """
    Fetches available flavors, allowable batch quantities, AI nudge rules,
    and current read-only wallet balance for Screen 5.
    """
    session_info = resolve_session_level(kid_session_id)
    level = session_info["level"]

    # 1. Read live wallet balance via WalletService (read-only, no deduction)
    wallet_balance = WalletService.get_balance(kid_session_id)

    # 2. Query Data Science tables if available
    try:
        # Check level_flavor_settings
        settings_res = (
            supabase.table("level_flavor_settings")
            .select("flavors_shown, max_flavors_selectable")
            .eq("level", level)
            .maybe_single()
            .execute()
        )
        max_flavors = (
            settings_res.data["max_flavors_selectable"]
            if settings_res.data and "max_flavors_selectable" in settings_res.data
            else (2 if level <= 2 else 3)
        )

        # Check options table for flavors and quantities
        decisions_res = (
            supabase.table("decisions")
            .select("decision_id, decision_code")
            .eq("level", level)
            .execute()
        )
        decision_map = {d["decision_code"]: d["decision_id"] for d in (decisions_res.data or [])}

        flavor_options = []
        quantity_options = []

        if "FLAVOR" in decision_map:
            f_res = (
                supabase.table("options")
                .select("option_code, display_label, base_cost")
                .eq("decision_id", decision_map["FLAVOR"])
                .execute()
            )
            for f in f_res.data or []:
                flavor_options.append(
                    FlavorOption(
                        id=f["option_code"],
                        name=f["display_label"],
                        color_hex="#E63946",
                        is_unlocked=True,
                    )
                )

        if "QUANTITY" in decision_map:
            q_res = (
                supabase.table("options")
                .select("option_code, display_label, serving_capacity")
                .eq("decision_id", decision_map["QUANTITY"])
                .execute()
            )
            for q in q_res.data or []:
                # Extract numeric units or default
                units = int(q.get("serving_capacity") or 20)
                quantity_options.append(
                    QuantityOption(
                        units=units,
                        label=q["display_label"],
                        is_recommended=(units <= 25),
                    )
                )

        # Check nudge_content
        nudges_res = (
            supabase.table("nudge_content")
            .select("nudge_id, decision_code, tip_text")
            .eq("level", level)
            .eq("status", "approved")
            .execute()
        )
        nudge_rules = []
        for n in nudges_res.data or []:
            nudge_rules.append(
                NudgeRule(
                    rule_id=f"nudge_{n['nudge_id']}",
                    trigger_type="decision_hint",
                    copy_text=n["tip_text"],
                )
            )

        # If DS tables returned full options, use them
        if flavor_options and quantity_options:
            return Screen5OptionsResponse(
                kid_session_id=UUID(str(kid_session_id)),
                level=level,
                wallet_balance_cents=wallet_balance,
                max_flavors_allowed=max_flavors,
                flavor_options=flavor_options,
                quantity_options=quantity_options,
                nudge_rules=nudge_rules,
                data_source="ds_confirmed",
            )
    except Exception:
        pass  # Seamless fallback to mock provider

    # 3. Fallback to MockFlavorQuantityProvider (explicitly authorized by PRD/Jira)
    fallback_data = MockFlavorQuantityProvider.get_options_for_level(level)
    return Screen5OptionsResponse(
        kid_session_id=UUID(str(kid_session_id)),
        level=level,
        wallet_balance_cents=wallet_balance,
        max_flavors_allowed=fallback_data["max_flavors"],
        flavor_options=fallback_data["flavors"],
        quantity_options=fallback_data["quantities"],
        nudge_rules=fallback_data["nudges"],
        data_source="mock_fallback",
    )


@router.post("/decisions", response_model=Screen5DecisionResponse)
def submit_screen_5_decision(payload: Screen5DecisionRequest):
    """
    Validates inventory choices against player's level constraints,
    persists structured JSONB to decision_log, and routes to Screen 6.
    """
    session_info = resolve_session_level(str(payload.kid_session_id))
    level = session_info["level"]

    # Level-based max flavor limit
    max_flavors = 2 if level <= 2 else 3
    if len(payload.selected_flavors) > max_flavors:
        raise HTTPException(
            status_code=400,
            detail=f"Exceeded max allowed flavors ({max_flavors}) for Level {level}",
        )

    # Validate batch quantity against allowed choices
    allowed_quantities = {
        1: [20, 40, 60],
        2: [25, 50, 100],
        3: [30, 60, 120],
    }
    level_allowed = allowed_quantities.get(level, [20, 40, 60])
    if payload.batch_quantity not in level_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid batch quantity {payload.batch_quantity}. Must be one of: {level_allowed}",
        )

    # Build structured JSONB payload
    persisted_payload = Screen5PersistedPayload(
        selected_flavors=payload.selected_flavors,
        flavor_count=len(payload.selected_flavors),
        batch_quantity=payload.batch_quantity,
        nudge_fired_id=payload.nudge_fired_id,
    )

    # Persist into decision_log
    insert_res = (
        supabase.table("decision_log")
        .insert({
            "kid_session_id": str(payload.kid_session_id),
            "screen_id": "screen_5",
            "decision_key": "flavor_quantity",
            "decision_value": "QUANTITY_FLAVOR",
            "value_jsonb": persisted_payload.model_dump(),
            "source_screen": "screen_5",
        })
        .execute()
    )

    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Failed to save decision to decision_log")

    decision_id = insert_res.data[0]["id"]

    return Screen5DecisionResponse(
        status="success",
        decision_id=UUID(str(decision_id)),
        kid_session_id=payload.kid_session_id,
        screen_id="screen_5",
        persisted_payload=persisted_payload,
        next_screen="screen_6",
    )


@router.get("/decisions/{kid_session_id}", response_model=Screen5DecisionStateResponse)
def get_screen_5_decision(kid_session_id: str):
    """
    Retrieves the latest persisted decision for Screen 5 to support back-navigation / page reload.
    """
    res = (
        supabase.table("decision_log")
        .select("id, value_jsonb, created_at")
        .eq("kid_session_id", str(kid_session_id))
        .eq("decision_key", "flavor_quantity")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not res.data:
        return Screen5DecisionStateResponse(has_decision=False)

    row = res.data[0]
    payload = Screen5PersistedPayload(**row["value_jsonb"]) if row.get("value_jsonb") else None

    return Screen5DecisionStateResponse(
        has_decision=True,
        decision_id=UUID(str(row["id"])),
        persisted_payload=payload,
        created_at=str(row.get("created_at")),
    )
