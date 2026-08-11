```python
import os


# =========================
# Telegram
# =========================

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

OWNER_ID: int = int(
    os.getenv("OWNER_ID", "0")
)


# =========================
# Gifts Intelligence
# =========================

SUPABASE_URL: str = os.getenv(
    "SUPABASE_URL",
    ""
)

SUPABASE_KEY: str = os.getenv(
    "SUPABASE_KEY",
    ""
)

PAYMENT_BOT_USERNAME: str = os.getenv(
    "PAYMENT_BOT_USERNAME",
    "vsdvscbot"
)
```
