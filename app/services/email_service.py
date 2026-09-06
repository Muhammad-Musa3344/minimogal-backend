import resend
from app.config import RESEND_API_KEY, RESEND_FROM_EMAIL, FRONTEND_ORIGIN
from app.db.supabase_client import supabase

resend.api_key = RESEND_API_KEY



def generate_custom_magic_link(email: str):
    response = supabase.auth.admin.generate_link({
        "type":"signup",
        "email": email,
        "options": {
            "redirect_to": f"{FRONTEND_ORIGIN}/auth/confirm"
        }})
    magic_link = response.properties.action_link
    return magic_link


def send_magic_link_email(to_email: str):
    magic_link = generate_custom_magic_link(to_email)
    resend.Emails.send({
        "from": RESEND_FROM_EMAIL,
        "to": to_email,
        "subject": "Confirm your Mogul Mind account",
        "html": f"<p>Click below to confirm your account:</p><a href='{magic_link}'>Confirm my account</a>",
    }) 



def send_parent_report_email(to_email: str, report_text: str):
    resend.Emails.send({
        "from": RESEND_FROM_EMAIL,
        "to": to_email,
        "subject": "Your child's Mogul Mind session report",
        "html": f"<h2>How today's session went</h2><p>{report_text}</p>",
    })