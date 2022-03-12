# GGSheet manager
# | IMPORT
import base64
import os
import pickle
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from typing import List
from urllib.error import HTTPError

from parseHTML import parseHTML

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
SHEET_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.path.join(os.path.split(sys.argv[0])[0], "key.json")

SHEET_CREDS = None
SHEET_CREDS = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SHEET_SCOPES
)

GMAIL_SCOPES = ["https://mail.google.com/"]

CREDENTIALS_FILENAME = os.path.join(os.path.split(sys.argv[0])[0], "credentials.json")
TOKEN_FILENAME = os.path.join(os.path.split(sys.argv[0])[0], "token.pickle")

GMAIL_CREDS = None
if os.path.exists(TOKEN_FILENAME):
    with open(TOKEN_FILENAME, "rb") as token:
        GMAIL_CREDS = pickle.load(token)
if not GMAIL_CREDS or not GMAIL_CREDS.valid:
    if GMAIL_CREDS and GMAIL_CREDS.expired and GMAIL_CREDS.refresh_token:
        GMAIL_CREDS.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILENAME, GMAIL_SCOPES)
        GMAIL_CREDS = flow.run_local_server(port=0)

    with open(TOKEN_FILENAME, "wb") as token:
        pickle.dump(GMAIL_CREDS, token)

# | CLASSES

class sheet_management:
    def __init__(self, sheet_id: str, creds: service_account.Credentials) -> None:
        self.sheet_id = sheet_id
        self.service = self.build_service(creds)

    def build_service(self, creds):
        return build("sheets", "v4", credentials=creds)

    def read_sheet_by_range(self, _range: str):
        sheet = self.service.spreadsheets()
        return sheet.values().get(spreadsheetId=self.sheet_id, range=_range).execute()

    def write_sheet_by_range(
        self, _range: str, content: List[str], input_mode: str = "RAW"
    ):
        sheet = self.service.spreadsheets()
        return (
            sheet.values()
            .update(
                spreadsheetId=self.sheet_id,
                range=_range,
                valueInputOption=input_mode,
                body={"values": content},
            )
            .execute()
        )

class gmail_management:
    def __init__(self, creds: service_account.Credentials) -> None:
        self.service = self.build_service(creds)

    def build_service(self, creds):
        return build("gmail", "v1", credentials=creds)

    def create_message(self, receiver, subject, text):
        message = MIMEMultipart()
        message["to"] = receiver
        message["subject"] = subject

        msg = MIMEText(text, "html")
        message.attach(msg)

        return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_mail(self, to: str, subject: str, otp: str, ref: str) -> None:
        r_msg = parseHTML(os.path.abspath(r"D:\TEDxKasetsartU\Discord\regis-discord-bot\googleModule\content.html"), {"OTP":otp, "REF":ref})
        content = self.create_message(to, subject, r_msg)
        try:
            res = self.service.users().messages().send(userId="ratcahpol.c@ku.th", body=content).execute()
            return res
        except HTTPError as error:
            print(f"Error\n\n{error}")
            return None

# | MAIN
if __name__ == "__main__":
    # s = sheet_management(sheet_id="1V1jUG9ZSRJm3rjWpf2zySVLv6qjURgDGazl98y6ECTo", creds=SHEET_CREDS)
    # print(s.read_sheet_by_range("media อันแรก!A1:X11"))
    sys.path.append(os.path.abspath(r"D:\TEDxKasetsartU\Discord\regis-discord-bot\utils"))
    from OTP import gen_otp
    g = gmail_management(creds=GMAIL_CREDS)
    otp, ref = gen_otp()
    print(g.send_mail("ratcahpol.c@ku.th", "Test", otp, ref))