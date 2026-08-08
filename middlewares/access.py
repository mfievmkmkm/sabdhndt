from typing import Callable, Dict, Any, Awaitable
from datetime import datetime
import os
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.enums.chat_member_status import ChatMemberStatus

import config
import database as db
from keyboards.inline import get_subscription_keyboard


# Файл с подписками от платёжного бота
SUBSCRIPTIONS_FILE = r"C:\Users\kucan\SellPrivate_Bot\subscriptions.txt"


def is_user_subscribed(user_id: int) -> bool:
    """Проверяет, есть ли у пользователя активная подписка"""
    try:
        with open(SUBSCRIPTIONS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 2:
                    uid, expires = parts
                    if int(uid) == user_id:
                        return datetime.fromisoformat(expires) > datetime.now()
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return False


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Админ всегда имеет доступ
        if user_id == config.OWNER_ID:
            return await handler(event, data)

        # Проверяем, не заблокирован ли пользователь
        if await db.is_user_blocked(user_id):
            return

        # Проверяем платную подписку
        if not is_user_subscribed(user_id):
            text = (
                "💎 <b>Доступ к боту только для подписчиков!</b>\n\n"
                "Оформите подписку у нашего платёжного бота:\n"
                "👉 @твой_платёжный_бот\n\n"
                "После оплаты доступ откроется автоматически."
            )
            keyboard = None

            if isinstance(event, Message):
                await event.answer(text, parse_mode="HTML", reply_markup=keyboard)
            elif isinstance(event, CallbackQuery):
                await event.answer("Доступ только для подписчиков.", show_alert=True)
                await event.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
            return

        # Проверяем подписку на канал (если настроена)
        channel_username = await db.get_subscription_channel()

        if not channel_username:
            return await handler(event, data)

        bot: Bot = data['bot']

        try:
            member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
            if member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR
            ]:
                return await handler(event, data)
        except Exception:
            pass

        text = f"Для использования бота необходимо подписаться на канал: {channel_username}"
        keyboard = get_subscription_keyboard(channel_username)

        if isinstance(event, Message):
            await event.answer(text, reply_markup=keyboard)
        elif isinstance(event, CallbackQuery):
            await event.answer("Сначала подпишитесь на канал.", show_alert=True)
            await event.message.answer(text, reply_markup=keyboard)