import os
import os.path
import pickle

import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from const import BANK_CLIENT_SECRET_FILE, BANK_SCOPES, SERVICE_ACCOUNT_FILE, BANK_AUTH_CREDENTIALS_DAT, \
    MESSAGE_AUTH_CREDENTIALS_DAT, MESSAGE_CLIENT_SECRET_FILE, MESSAGE_SCOPES


def __get_gmail_service(auth_credentials_dat, client_secret_file, scopes):
    if not os.path.exists(auth_credentials_dat):
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        credentials = flow.run_local_server()
        with open(auth_credentials_dat, 'wb') as credentials_dat:
            pickle.dump(credentials, credentials_dat)
    else:
        with open(auth_credentials_dat, 'rb') as credentials_dat:
            credentials = pickle.load(credentials_dat)
    if credentials.expired:
        credentials.refresh(Request())

    return build('gmail', 'v1', credentials=credentials, cache_discovery=False)


def get_bank_gmail_service():
    return __get_gmail_service(BANK_AUTH_CREDENTIALS_DAT, BANK_CLIENT_SECRET_FILE, BANK_SCOPES)


def get_message_gmail_service():
    return __get_gmail_service(MESSAGE_AUTH_CREDENTIALS_DAT, MESSAGE_CLIENT_SECRET_FILE, MESSAGE_SCOPES)


def get_gspread_service():
    return gspread.service_account(SERVICE_ACCOUNT_FILE)
