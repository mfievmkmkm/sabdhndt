import asyncio
from datetime import datetime, timezone

from supabase import Client, create_client


class SubscriptionService:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    async def _run(self, fn):
        return await asyncio.to_thread(fn)

    async def has_active_subscription(self, telegram_id: int) -> bool:

        def op():
            users = (
                self.client
                .table("users")
                .select("id")
                .eq("telegram_id", telegram_id)
                .limit(1)
                .execute()
                .data
            )

            if not users:
                return False

            user_id = users[0]["id"]

            subscriptions = (
                self.client
                .table("subscriptions")
                .select("id, expires_at")
                .eq("user_id", user_id)
                .eq("status", "active")
                .order("expires_at", desc=True)
                .limit(1)
                .execute()
                .data
            )

            if not subscriptions:
                return False

            expires_at = subscriptions[0].get("expires_at")

            if not expires_at:
                return False

            expires = datetime.fromisoformat(
                expires_at.replace("Z", "+00:00")
            )

            return expires > datetime.now(timezone.utc)

        return await self._run(op)
