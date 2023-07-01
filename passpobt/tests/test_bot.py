import time
import asyncio
from datetime import datetime

import pytest

from passpobt import bot, mailbox
from passpobt.bot import NotificationsBot
from passpobt.telegram import TelegramBot


DAY = 24 * 60 * 60


@pytest.mark.asyncio
async def test_message_per_trigger(monkeypatch):
    """Test if only one message is sent for each trigger."""
    messages_sent = 0
    trigger_time_requests = 0

    class EnoughCycles(BaseException):
        """Raised when bot has run for too long."""

    async def _message_counter(*args, **kwargs):
        nonlocal messages_sent
        messages_sent += 1

    def _get_last_trigger_message_time():
        nonlocal trigger_time_requests
        trigger_time_requests += 1
        if trigger_time_requests > 5:
            raise EnoughCycles()
        return datetime.fromtimestamp(0)

    monkeypatch.setattr(mailbox, 'last_trigger_message_time', _get_last_trigger_message_time)
    monkeypatch.setattr(bot, 'LOOP_DELAY', 0)
    monkeypatch.setattr(TelegramBot, 'send_notification', _message_counter)
    notifications_bot = NotificationsBot()
    bot_task = asyncio.create_task(notifications_bot.run())
    with pytest.raises(EnoughCycles):
        await bot_task
    assert messages_sent == 1
    assert trigger_time_requests > 5


@pytest.mark.asyncio
async def test_several_days(monkeypatch):
    """Run bot for several days and verify the amount of messages sent."""
    # pylint: disable=too-many-locals
    messages_sent = 0
    trigger_time_requests = 0
    days_passed = 0
    expected_days = 365
    mailbox_checks_per_day = 10

    async def _message_counter(*args, **kwargs):
        nonlocal messages_sent
        messages_sent += 1

    class Apocalypse(BaseException):
        """Time has run out and we are all doomed."""

    def each_10_checks_day_passes():
        """Every 10 checks a day passes."""
        t = 0
        nonlocal days_passed
        while days_passed < expected_days:
            for _ in range(mailbox_checks_per_day):
                yield datetime.fromtimestamp(t)
            t += DAY
            days_passed += 1

    triggers_schedule = each_10_checks_day_passes()

    def _get_last_trigger_message_time():
        nonlocal trigger_time_requests
        trigger_time_requests += 1
        try:
            return next(triggers_schedule)
        except StopIteration as ex:
            raise Apocalypse() from ex

    def each_day():
        """Between each call of the `datetime.now` there is 5 minutes of virtual time."""
        t = 0
        while True:
            yield t
            t += DAY

    now_schedule = each_day()

    def virtual_time(*args, **kwargs):
        return next(now_schedule)

    monkeypatch.setattr(mailbox, 'last_trigger_message_time', _get_last_trigger_message_time)
    monkeypatch.setattr(bot, 'LOOP_DELAY', 0)
    monkeypatch.setattr(TelegramBot, 'send_notification', _message_counter)
    monkeypatch.setattr(time, 'time', virtual_time)
    notifications_bot = NotificationsBot()
    bot_task = asyncio.create_task(notifications_bot.run())
    with pytest.raises(Apocalypse):
        await bot_task
    assert messages_sent == days_passed == expected_days
    assert trigger_time_requests == expected_days * mailbox_checks_per_day + 1
