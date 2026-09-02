import hashlib

def generate_seed(avatar_id: str, playthrough_index: int) -> str:
    """Deterministic seed — same inputs always produce the same seed."""
    raw = f"{avatar_id}:{playthrough_index}"
    return hashlib.sha256(raw.encode()).hexdigest()