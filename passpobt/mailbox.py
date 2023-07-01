import os.path
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authorize() -> Credentials:
    """Authorize Google API and return credentials for API calls."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.getenv('CREDENTIALS_PATH'), SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf8') as token:
            token.write(creds.to_json())
    return creds


def last_trigger_message_time() -> datetime | None:
    """Return UTC time when last trigger message was received or None if there are no trigger messages."""
    # pylint: disable=no-member
    creds = authorize()
    service = build('gmail', 'v1', credentials=creds)
    messages = service.users().messages() \
        .list(userId='me', labelIds=['INBOX'], maxResults=1, q="subject:\"ЛИСТ ОЖИДАНИЯ САЙТА ЗАПИСИ\"") \
        .execute()
    if not messages['messages']:
        return None
    message_id = messages['messages'][0]['id']
    message = service.users().messages().get(userId='me', id=message_id, format="metadata").execute()
    for header in message['payload']['headers']:
        if header['name'] == 'Date':
            message_received_at = datetime.strptime(header['value'], '%d %b %Y %H:%M:%S %z')
    return message_received_at.astimezone(tz=timezone.utc)
