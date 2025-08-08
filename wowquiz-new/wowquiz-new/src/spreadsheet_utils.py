import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_sheets(credentials_file, spreadsheet_id):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id)

def ensure_id_column(sheet):
    header = sheet.row_values(1)
    try:
        idx_nagr = next(i for i, val in enumerate(header) if val.strip().lower() == 'награждение')
    except StopIteration:
        idx_nagr = None
    if 'ID' not in [h.strip().upper() for h in header]:
        insert_at = (idx_nagr + 2) if idx_nagr is not None else (len(header) + 1)
        sheet.add_cols(1)
        sheet.update_cell(1, insert_at, 'ID')