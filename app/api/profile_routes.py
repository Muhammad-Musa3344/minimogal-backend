from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Any
from app.db.supabase_client import supabase
from app.middleware.auth import require_auth

router = APIRouter(prefix="/api/profile", tags=["profile"])


class UpdateProfileRequest(BaseModel):
    kid_session_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    avatar_config: Optional[dict[str, Any]] = None


def resolve_age_tier(age: int) -> str:
    """Maps a kid's age to the correct tier using DS's age_level_mapping table."""
    result = (
        supabase.table("age_level_mapping")
        .select("level, min_age, max_age")
        .lte("min_age", age)
        .gte("max_age", age)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=400, detail=f"No age tier mapping found for age {age}")

    level = result.data[0]["level"]
    tier_map = {1: "7-8", 2: "9-10", 3: "11-12"}
    return tier_map.get(level, "7-8")


@router.patch("/update")
def update_profile(payload: UpdateProfileRequest, account_id: str = Depends(require_auth)):
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

    update_data = {}
    if payload.name is not None:
        update_data["name"] = payload.name
    if payload.avatar_config is not None:
        update_data["avatar_config"] = payload.avatar_config
    if payload.age is not None:
        if not (7 <= payload.age <= 14):
            raise HTTPException(status_code=400, detail="Age must be 7-14")
        update_data["age"] = payload.age
        update_data["age_tier"] = resolve_age_tier(payload.age)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        supabase.table("kid_session")
        .update(update_data)
        .eq("id", payload.kid_session_id)
        .execute()
    )

    return {"success": True, "kid_session": result.data[0]}


@router.get("/{kid_session_id}")
def get_profile(kid_session_id: str, account_id: str = Depends(require_auth)):
    result = (
        supabase.table("kid_session")
        .select("id, name, age, age_tier, avatar_config")
        .eq("id", kid_session_id)
        .eq("household_id", account_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Kid session not found")
    return result.data