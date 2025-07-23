import gspread
from google.oauth2.service_account import Credentials

def log_to_gsheet(data, quotes, summary):

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("/etc/secrets/creds.json", scopes=scopes)
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
