import os
import pickle

import googleapiclient.discovery
import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from const import SCOPES, CLIENT_SECRET_FILE, SERVICE_ACCOUNT_FILE


def get_gmail_service():
    creds = None

    if os.path.exists("auth/token.pickle"):
        with open("auth/token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open("auth/token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return googleapiclient.discovery.build('gmail', 'v1', credentials=creds)


def get_gspread_service():
    return gspread.service_account(SERVICE_ACCOUNT_FILE)
