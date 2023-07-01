import os

from aiogram import Bot


class TelegramBot:
    """Telegram bot for sending notifications."""

    def __init__(self):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot = Bot(token=token)

    async def send_notification(self):
        """Send notification to telegram chat."""
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        await self.bot.send_message(
            chat_id=chat_id,
            text='⚡It\'s time to update application!⚡'
        )
