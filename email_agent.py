import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

class EmailAgent:
    def __init__(self):
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth"""
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("⚠️ credentials.json not found! Gmail features disabled.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail connected!")

    def send_email(self, to, subject, body):
        """Send an email"""
        if not self.service:
            return "Gmail is not connected. Please check credentials.json."
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return f"Email sent to {to} successfully!"
        except Exception as e:
            return f"Failed to send email: {str(e)}"

    def read_latest_emails(self, count=5):
        """Read latest emails from inbox"""
        if not self.service:
            return []
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=count,
                labelIds=['INBOX']
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages[:count]:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = msg_data['payload']['headers']
                email_info = {}
                for header in headers:
                    if header['name'] in ['From', 'Subject', 'Date']:
                        email_info[header['name']] = header['value']
                emails.append(email_info)

            return emails
        except Exception as e:
            print(f"Read email error: {e}")
            return []

    def get_unread_count(self):
        """Get number of unread emails"""
        if not self.service:
            return 0
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD']
            ).execute()
            return results.get('resultSizeEstimate', 0)
        except:
            return 0
