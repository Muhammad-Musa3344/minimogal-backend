from app.db.supabase_client import supabase
from app.services.email_service import send_parent_report_email

def on_playthrough_complete(playthrough_id: str):
    """Fires when a playthrough ends. Fetches decision log, generates
    the parent report, and emails it. Report content is a placeholder
    until DS5.1 (report structure) and the model router are fully wired
    together in a later sprint."""
    playthrough = (
        supabase.table("playthroughs")
        .select("*, child_profiles(account_id, accounts(email))")
        .eq("id", playthrough_id)
        .maybe_single()
        .execute()
    )
    if not playthrough.data:
        return

    report_text = "Your child completed a full day running their lollipop stand!"

    parent_email = playthrough.data["child_profiles"]["accounts"]["email"]
    send_parent_report_email(parent_email, report_text)