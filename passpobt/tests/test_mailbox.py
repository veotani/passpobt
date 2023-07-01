from datetime import datetime

from passpobt import mailbox


def test_authorize():
    """Test if credentials are valid."""
    creds = mailbox.authorize()
    assert creds.valid


def test_get_latest_notification_timestamp():
    """Test if notification timestamp is within last 24hr."""
    t = mailbox.last_trigger_message_time()
    if t:
        assert t <= datetime.now().astimezone(t.tzinfo)
