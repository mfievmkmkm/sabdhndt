from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import database as db
from services.subscription import SubscriptionService


subscription_service = SubscriptionService(
    config.SUPABASE_URL,
    config.SUPABASE_KEY,
)


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, Dict[str, Any]],
            Awaitable[Any]
        ],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:

        user_id = event.from_user.id

        # Администратор / владелец всегда имеет доступ
        if user_id == config.OWNER_ID:
            return await handler(event, data)

        # Проверяем локальную блокировку GiftHunter
        if await db.is_user_blocked(user_id):
            return

        # Проверяем подписку Gifts Intelligence через Supabase
        try:
            has_subscription = (
                await subscription_service.has_active_subscription(user_id)
            )
        except Exception as e:
            print(f"Subscription check error for {user_id}: {e}")

            # Если Supabase временно недоступен —
            # безопаснее не давать доступ.
            has_subscription = False

        if not has_subscription:
            payment_bot = getattr(
                config,
                "PAYMENT_BOT_USERNAME",
                "vsdvscbot",
            )

            text = (
                "🔒 <b>NFT-Tracker доступен только подписчикам "
                "Gifts Intelligence.</b>\n\n"
                "Для использования поиска подарков нужна активная "
                "подписка.\n\n"
                "После оплаты доступ откроется автоматически."
            )

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💎 Оформить подписку",
                            url=f"https://t.me/{payment_bot.lstrip('@')}",
                        )
                    ]
                ]
            )

            if isinstance(event, Message):
                await event.answer(
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )

            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🔒 Нужна активная подписка Gifts Intelligence.",
                    show_alert=True,
                )

                if event.message:
                    await event.message.answer(
                        text,
                        parse_mode="HTML",
                        reply_markup=keyboard,
                    )

            return

        # Подписка активна — разрешаем работу GiftHunter
        return await handler(event, data)
