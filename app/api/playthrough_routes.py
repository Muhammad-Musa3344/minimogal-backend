from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.supabase_client import supabase
from app.middleware.auth import require_auth
from app.engine.engine import run_engine

router = APIRouter(prefix="/api/playthroughs", tags=["playthroughs"])

class CreatePlaythroughRequest(BaseModel):
    child_id: str
    business: str = "lollipop_stand"
    level: int = 1

@router.post("")
def create_playthrough(payload: CreatePlaythroughRequest, account_id: str = Depends(require_auth)):
    child = (
        supabase.table("child_profiles")
        .select("id")
        .eq("id", payload.child_id)
        .eq("account_id", account_id)
        .maybe_single()
        .execute()
    )
    if not child.data:
        raise HTTPException(status_code=404, detail="Child profile not found")

    result = supabase.table("playthroughs").insert({
        "child_id": payload.child_id,
        "business": payload.business,
        "level": payload.level,
    }).execute()

    return result.data[0]


class ResolvePlaythroughRequest(BaseModel):
    avatar_id: str
    playthrough_index: int
    quantity: int
    flavors: list[str]
    sourcing_method: str
    price_slot: int
    location: str
    time_weather: str
    advertising: str
    level: int = 1

@router.post("/{playthrough_id}/resolve")
def resolve_playthrough(
    playthrough_id: str,
    payload: ResolvePlaythroughRequest,
    account_id: str = Depends(require_auth),
):
    result = run_engine(
        avatar_id=payload.avatar_id,
        playthrough_index=payload.playthrough_index,
        quantity=payload.quantity,
        flavors=payload.flavors,
        sourcing_method=payload.sourcing_method,
        price_slot=payload.price_slot,
        location=payload.location,
        time_weather=payload.time_weather,
        advertising=payload.advertising,
        level=payload.level,
    )

    supabase.table("playthroughs").update({
        "status": "complete_profit" if result["outcome"] == "profit" else "complete_loss",
        "seed": result["seed"],
        "completed_at": "now()",
    }).eq("id", playthrough_id).execute()

    return result