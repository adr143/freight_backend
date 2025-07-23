import gspread
from oauth2client.service_account import ServiceAccountCredentials

def log_to_gsheet(data, quotes, summary):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("QuoteLog").sheet1

    for q in quotes:
        sheet.append_row([
            data["origin"], data["destination"], q["vendor"],
            q["rate"], q["final_rate"], q["margin"], summary
        ])
