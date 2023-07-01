# Passpobt

**Passpobt** (pronounced like "passport" but with a runny nose) is a simple bot that checks your Gmail for messages from
midpass. It reminds you to approve your application whenever possible. The only supported mailbox provider is Gmail.

## Problem

For Russian citizens, there is a website that allows you to apply for documents while abroad. The system is peculiar:
you must check in daily to show you're still in queue for the desired document.

The website uses CAPTCHA to prevent software log-ins and sometimes changes your password. This, and the uncertainty of
the process when it's my turn to retrieve the documents, led me to conclude that making this fully autonomous would take
three to five times longer to implement.

I've simplified this bot to serve only one user. I didn't want to deal with multiple users and various mailbox
providers. Though feasible via SMTP/POP3/IMAP, using the Google API here is both convenient and time-saving.

After you check in, you receive an email with the same subject. A 24-hour cooldown period then begins. This is why I
can't just stop visiting the website, for example, every morning, because the cooldown window shifts.

To help remember to do this, the bot sends a notification 24 hours after my last check-in.

## Usage

Create a `.env` file as per the provided example. You will need Google credentials, so please follow
[this guide](https://developers.google.com/gmail/api/quickstart/python#set_up_your_environment) to get them.

- `TELEGRAM_BOT_TOKEN` - Create a Telegram bot in BotFather
- `TELEGRAM_CHAT_ID` - ID of the chat between you and the bot
- `CREDENTIALS_PATH` - The file you download by following Google's guide

To verify everything works, you can run tests. They send you a Telegram message to confirm everything is properly set up
on the Telegram side with your parameters.
