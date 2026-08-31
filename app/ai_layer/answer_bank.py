import hashlib
import json
from app.db.supabase_client import supabase

def _hash_input(structured_input: dict) -> str:
    return hashlib.sha256(json.dumps(structured_input, sort_keys=True).encode()).hexdigest()

def lookup_answer_bank(touchpoint: str, structured_input: dict):
    """Check for pre-generated, QA'd content before ever calling a live model."""
    input_hash = _hash_input(structured_input)
    result = (
        supabase.table("answer_bank")
        .select("approved_text, audio_url")
        .eq("touchpoint", touchpoint)
        .eq("input_state_hash", input_hash)
        .eq("status", "approved")
        .maybe_single()
        .execute()
    )
    return result.data