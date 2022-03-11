# GGSheet manager
# | IMPORT
import os
import sys

from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import List

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.path.join("ggsheet", "key.json")

CREDS = None
CREDS = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

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

# | MAIN
if __name__ == "__main__":
    s = sheet_management(sheet_id="1V1jUG9ZSRJm3rjWpf2zySVLv6qjURgDGazl98y6ECTo", creds=CREDS)
    print(s.read_sheet_by_range("media อันแรก!A1:X11"))