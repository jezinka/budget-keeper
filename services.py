import gspread
import os
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from const import CLIENT_SECRET_FILE, SCOPES, SERVICE_ACCOUNT_FILE, HINT_EMAIL, AUTH_CREDENTIALS_DAT


def get_gmail_service():
    if not os.path.exists(AUTH_CREDENTIALS_DAT):
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        authorization_url, state = flow.authorization_url(access_type='offline', login_hint=HINT_EMAIL,
                                                          include_granted_scopes='true')
        credentials = flow.run_local_server()
        with open(AUTH_CREDENTIALS_DAT, 'wb') as credentials_dat:
            pickle.dump(credentials, credentials_dat)
    else:
        with open(AUTH_CREDENTIALS_DAT, 'rb') as credentials_dat:
            credentials = pickle.load(credentials_dat)
    if credentials.expired:
        credentials.refresh(Request())

    return build('gmail', 'v1', credentials=credentials)


def get_gspread_service():
    return gspread.service_account(SERVICE_ACCOUNT_FILE)
