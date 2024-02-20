import os
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from const import BANK_CLIENT_SECRET_FILE, BANK_SCOPES, BANK_AUTH_CREDENTIALS_DAT


def get_bank_gmail_service():
    if not os.path.exists(BANK_AUTH_CREDENTIALS_DAT):
        flow = InstalledAppFlow.from_client_secrets_file(BANK_CLIENT_SECRET_FILE, BANK_SCOPES)
        flow.authorization_url(access_type='offline', include_granted_scopes='true')
        credentials = flow.run_local_server()
        with open(BANK_AUTH_CREDENTIALS_DAT, 'wb') as credentials_dat:
            pickle.dump(credentials, credentials_dat)
    else:
        with open(BANK_AUTH_CREDENTIALS_DAT, 'rb') as credentials_dat:
            credentials = pickle.load(credentials_dat)
    if credentials.expired:
        credentials.refresh(Request())

    return build('gmail', 'v1', credentials=credentials, cache_discovery=False)
