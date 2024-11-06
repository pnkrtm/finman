import pandas as pd

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Словарь для перевода чисел в буквы
charstr='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
chars=list(charstr)
nums=[i for i in range(1,53)]
orddict=dict(zip(nums, chars))


class GSheetWorker:
    def __init__(self, credentials_file) -> None:
        self.creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        self.service = build('sheets', 'v4', credentials=self.creds)

    def get_df(self, spreadsheet_id, sheet_name):
        sheet = self.service.spreadsheets()
        range_name = f"{sheet_name}!A1:Z"
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        google_sheet_df = pd.DataFrame(values[1:], columns=values[0])

        return google_sheet_df
    
    def insert_df(self, missing_records: pd.DataFrame, spreadsheet_id, sheet_name):
        sheet = self.service.spreadsheets()
        new_values = missing_records.values.tolist()

        body = {
            'values': new_values
        }
        
        last_col = orddict[missing_records.shape[1]]
        range_name = f"{sheet_name}!A1:{last_col}"

        append_result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
