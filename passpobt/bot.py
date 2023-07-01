import asyncio
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from rich.logging import RichHandler

from passpobt import mailbox
from passpobt.telegram import TelegramBot


load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
LOOP_DELAY = 5 * 60  # 5 minutes


class NotificationsBot:
    """Bot for sending notifications to users."""

    def __init__(self):
        """
        Initialize bot.

        Parameters
        ----------
        last_trigger_message_time : datetime
            When last trigger message was received. Notifications are only sent if there is a trigger message received
            after the last_trigger_message_time.
        """
        self._notification_task = None
        self._last_task_trigger = None
        self.bot = TelegramBot()

    async def run(self):
        """Start checking user emails and sending notifications on new trigger messages."""
        while True:
            try:
                trigger_time = mailbox.last_trigger_message_time()
                if trigger_time is None and self._last_task_trigger is None:
                    logging.info('No trigger messages found, waiting for one')
                elif self._last_task_trigger is None or trigger_time > self._last_task_trigger:
                    logging.info('Trigger message received, scheduling notification')
                    if self._notification_task is not None:
                        self._notification_task.cancel()
                        await self._notification_task
                    self._notification_task = asyncio.create_task(self._send_notification(trigger_time))
                    self._last_task_trigger = trigger_time
            except Exception:  # pylint: disable=broad-except
                logger.exception('Unhandled exception in notifications bot')
            await asyncio.sleep(LOOP_DELAY)

    async def _send_notification(self, trigger_time: datetime):
        """Send notification to user."""
        try:
            now = datetime.now(tz=trigger_time.tzinfo)
            assert trigger_time < now
            send_in = max(((trigger_time + timedelta(days=1)) - now).total_seconds(), 0)
            logger.info('Sending notification in %s seconds', int(send_in))
            await asyncio.sleep(send_in)
            await self.bot.send_notification()
        except asyncio.CancelledError:
            logger.info('Notification task cancelled')


async def run():
    """Run notifications bot."""
    bot = NotificationsBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(run())
