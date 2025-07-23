import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

def log_to_gsheet(data, quotes, summary):
    # Load the base64-encoded creds from an environment variable
    creds_b64 = os.getenv("GOOGLE_CREDS_B64")
    if not creds_b64:
        raise ValueError("Missing GOOGLE_CREDS_B64 environment variable")

    creds_json = json.loads(base64.b64decode(creds_b64).decode())

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open("QuoteLog").sheet1

    for q in quotes:
        sheet.append_row([
            data["origin"],
            data["destination"],
            q["vendor"],
            q["rate"],
            q["final_rate"],
            q["margin"],
            summary
        ])
