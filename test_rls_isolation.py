# test_rls_isolation.py
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY

admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

client_a = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
client_b = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def signup_and_confirm(client, email, password):
    user_id = None
    try:
        result = client.auth.sign_up({"email": email, "password": password})
        user_id = result.user.id
    except Exception as e:
        print(f"{email} signup: {e} (might already exist, continuing)")

    users = admin_client.auth.admin.list_users()
    for u in users:
        if u.email == email:
            user_id = u.id
            if not u.email_confirmed_at:
                admin_client.auth.admin.update_user_by_id(u.id, {"email_confirm": True})
                print(f"Force-confirmed {email}")
            break

    # Ensure a households row exists (service_role bypasses RLS here, which is fine for setup)
    existing = admin_client.table("households").select("id").eq("id", user_id).execute()
    if not existing.data:
        admin_client.table("households").insert({
            "id": user_id,
            "email": email,
            "auth_provider": "email",
            "email_verified": True,
        }).execute()
        print(f"Created households row for {email}")

    return user_id


EMAIL_A = "rlsusera1@gmail.com"
PASSWORD_A = "TestPass123"
EMAIL_B = "rlsuserb1@gmail.com"
PASSWORD_B = "TestPass123"

user_a_id = signup_and_confirm(client_a, EMAIL_A, PASSWORD_A)
user_b_id = signup_and_confirm(client_b, EMAIL_B, PASSWORD_B)

session_a = client_a.auth.sign_in_with_password({"email": EMAIL_A, "password": PASSWORD_A})
print(f"User A signed in: {session_a.user.id}")

kid_a = client_a.table("kid_session").insert({
    "household_id": session_a.user.id,
    "name": "User A's Kid",
    "age": 8,
}).execute()
print(f"User A created kid_session: {kid_a.data}")

session_b = client_b.auth.sign_in_with_password({"email": EMAIL_B, "password": PASSWORD_B})
print(f"User B signed in: {session_b.user.id}")

result = client_b.table("kid_session").select("*").execute()
print(f"\nUser B's visible kid_session rows: {result.data}")

if len(result.data) == 0:
    print("\nPASS — RLS is working. User B cannot see User A's data.")
else:
    print("\n FAIL — RLS is NOT working. User B can see other users' data!")