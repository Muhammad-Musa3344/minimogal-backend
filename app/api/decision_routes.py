from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.supabase_client import supabase
from app.middleware.auth import require_auth


router = APIRouter(prefix="/api/decisions", tags=["decisions"])

class Decision(BaseModel):
    kid_session_id: str
    screen_id: str
    decision_key:str
    decision_value: str

class SetAllDecisionsRequest(BaseModel):
    decisions: list[Decision]

    

@router.post("/set-decision")
def set_decision(payload: Decision):
    decision = payload.model_dump()
    try:
        result = (supabase.table("decision_log")
                  .insert(decision)
                  .execute())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to save decision"
        )
    return {"success": True}




@router.post("/set-all-decisions")
def set_all_decisions(payload: SetAllDecisionsRequest):
    decisions = [decision.model_dump() for decision in  payload.decisions]
    try:
        results = (supabase.table("decision_log")
                   .insert(decisions)
                   .execute())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to save decisions"
        )
    return {"success": True}






@router.get("/get-decision/{kid_session_id}/{decision_key}")
def get_decisions(kid_session_id:str, decision_key:str):
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
def get_all_decisions(kid_session_id:str):
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



    