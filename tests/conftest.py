# tests/conftest.py
import os

# Set fallback environment variables for test execution
os.environ.setdefault("SUPABASE_URL", "https://mock-test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "mock-service-role-key-test")
os.environ.setdefault("SUPABASE_ANON_KEY", "mock-anon-key-test")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:5173")
