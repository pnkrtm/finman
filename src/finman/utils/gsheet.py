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
    
    def format_row_with_color(self, spreadsheet_id, sheet_name, row_index):
        # Convert row index to A1 notation for the entire row
        sheet = self.service.spreadsheets()
        row_range = f"{sheet_name}!A{row_index}:Z{row_index}"

        # Apply blue background to the specified row
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": self.get_sheet_id(spreadsheet_id, sheet_name),
                            "startRowIndex": row_index - 1,  # 0-indexed
                            "endRowIndex": row_index,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.87,
                                    "green": 0.87,
                                    "blue": 1.0
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor)",
                    }
                }
            ]
        }

        # Execute the batch update
        sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def insert_df(self, missing_records: pd.DataFrame, spreadsheet_id, sheet_name, time_col: str, date_col: str):
        min_dt_idx = missing_records[time_col].idxmin()

        missing_records[date_col] = missing_records[date_col].astype(str)
        missing_records[time_col] = missing_records[time_col].dt.strftime('%Y-%m-%d %H:%M')

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

        # Calculate the start and end row for the new data
        updates = append_result.get('updates', {})
        updated_rows = updates.get('updatedRows', 0)
        start_row = updates.get('updatedRange').split('!')[1].split(':')[0][1:]
        start_row = int(start_row)

        # Find the row with the minimum dt
        min_dt_row_index = min_dt_idx + start_row

        # Apply formatting to the row with the minimum dt
        self.format_row_with_color(spreadsheet_id, sheet_name, int(min_dt_row_index))

    def get_sheet_id(self, spreadsheet_id, sheet_name):
        # Retrieve the sheet ID for the given sheet name
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in sheet_metadata.get("sheets", []):
            if sheet.get("properties", {}).get("title") == sheet_name:
                return sheet.get("properties", {}).get("sheetId")
        raise ValueError(f"Sheet name {sheet_name} not found.")
