import anthropic
import requests
from app.config import ANTHROPIC_API_KEY, DEEPSEEK_API_KEY
from app.ai_layer.model_router import get_model_for_touchpoint
from app.ai_layer.vocab_tier_gate import check_word_allowed
from app.db.supabase_client import supabase
import hashlib
import json

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def _hash_input(structured_input: dict) -> str:
    return hashlib.sha256(json.dumps(structured_input, sort_keys=True).encode()).hexdigest()

def _deepseek_judge(text: str, level: int) -> bool:
    """Second-opinion safety check. Returns True if DeepSeek approves the text."""
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{
                "role": "user",
                "content": (
                    f"You are a child-safety judge for a level-{level} kids' game (ages 7-9). "
                    f"Reply with ONLY 'APPROVE' or 'REJECT'. Text: {text}"
                ),
            }],
        },
        timeout=10,
    )
    verdict = response.json()["choices"][0]["message"]["content"].strip().upper()
    return verdict == "APPROVE"

def generate_and_store_content(touchpoint: str, structured_input: dict, level: int, use_judge: bool = True) -> dict:
    model = get_model_for_touchpoint(touchpoint)

    response = client.messages.create(
        model=model,
        max_tokens=150,
        system=(
            "Output ONLY valid JSON: {\"text\": string}. "
            "Use vocabulary appropriate for a 7-9 year old. "
            "Never invent numbers not present in the input."
        ),
        messages=[{"role": "user", "content": json.dumps(structured_input)}],
    )

    raw_text = response.content[0].text if response.content[0].type == "text" else "{}"
    parsed = json.loads(raw_text)
    generated_text = parsed.get("text", "")

    words = generated_text.lower().replace(".", "").replace(",", "").split()
    for word in words:
        if not check_word_allowed(word, level):
            return {"status": "rejected", "reason": f"word '{word}' exceeds vocabulary tier for level {level}"}

    if use_judge:
        if not _deepseek_judge(generated_text, level):
            return {"status": "rejected", "reason": "DeepSeek judge rejected content"}

    input_hash = _hash_input(structured_input)
    supabase.table("answer_bank").insert({
        "touchpoint": touchpoint,
        "input_state_hash": input_hash,
        "approved_text": generated_text,
        "status": "approved",
    }).execute()

    return {"status": "approved", "text": generated_text}