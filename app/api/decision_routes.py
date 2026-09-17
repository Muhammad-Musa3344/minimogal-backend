from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.supabase_client import supabase
from app.middleware.auth import require_auth
from typing import Any

router = APIRouter(prefix="/api/decisions", tags=["decisions"])

class Decision(BaseModel):
    kid_session_id: str
    decision_key:str
    decision_value: str
    value_jsonb: dict[str, Any] | None = None
    source_screen: str | None = None

class SetAllDecisionsRequest(BaseModel):
    decisions: list[Decision]

    

@router.post("/set-decision")
def set_decision(payload: Decision, account_id:str= Depends(require_auth)):
    decision = payload.model_dump()
    try:
        result = (supabase.table("decision_log")
                  .upsert(
                      decision,
                      on_conflict="kid_session_id,decision_key")
                  .execute())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to save decision"
        )
    return {"success": True}




@router.post("/set-all-decisions")
def set_decision(payload: SetAllDecisionsRequest, account_id:str= Depends(require_auth)):
    decisions = [decision.model_dump() for decision in  payload.decisions]
    try:
        results = (supabase.table("decision_log")
                   .upsert(
                       decisions,
                    on_conflict="kid_session_id,decision_key"
                       )
                   .execute())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to save decisions"
        )
    return {"success": True}






@router.get("/get-decision/{kid_session_id}/{decision_key}")
def get_decisions(kid_session_id:str, decision_key:str, account_id:str = Depends(require_auth)):
    try:
        result = (supabase.table("decision_log")
                    .select("*")
                    .eq("kid_session_id", kid_session_id)
                    .eq("decision_key", decision_key)
                    .single()
                    .execute()
                    )
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = "Failed to get decision"
        )

    return {
        "success": True,
        "decision": result.data
        }


@router.get("/get-all-decisions/{kid_session_id}")
def get_all_decisions(kid_session_id:str, account_id:str=Depends(require_auth)):
    try:
        result = (supabase.table("decision_log")
                    .select("*")
                    .eq("kid_session_id", kid_session_id)
                    .execute()
                    )
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = "Failed to get decision"
        )
    return {
            "success": True,
            "decisions": result.data
            }



    