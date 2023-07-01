import pytest

from passpobt.telegram import TelegramBot


@pytest.mark.asyncio
async def test_send_message():
    """Manual test for sending message to telegram chat."""
    bot = TelegramBot()
    await bot.send_notification()
