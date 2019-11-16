from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from yaspin import yaspin
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def google_login():
    google_spinner = yaspin(text="Вход в google...")
    google_spinner.start()
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            google_spinner.text = "[Ожидание ответа Google OAuth...]"
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    google_spinner.text = ""
    google_spinner.ok("Вход в Google выполнен успешно")
    service = build('calendar', 'v3', credentials=creds)

    return service
