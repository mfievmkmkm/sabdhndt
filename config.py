import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

PAYMENT_BOT_USERNAME = os.getenv("PAYMENT_BOT_USERNAME")


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not OWNER_ID:
    raise RuntimeError("OWNER_ID is not set")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is not set")

if not PAYMENT_BOT_USERNAME:
    raise RuntimeError("PAYMENT_BOT_USERNAME is not set")
