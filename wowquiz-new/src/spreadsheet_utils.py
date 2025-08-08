import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_sheets(credentials_file, spreadsheet_id):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id)

def get_or_create_log_worksheet(spreadsheet, title="Логи", rows=1000, cols=20):
    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)

def find_game_worksheet(spreadsheet, theme, date_str, location=None, start_time=None):
    for ws in spreadsheet.worksheets():
        title = ws.title
        if (date_str and date_str in title) or (theme and theme.lower() in title.lower()):
            if location and location.lower() in title.lower():
                return ws
            if not location:
                return ws
    return None

def append_row_by_order(ws, data_dict, column_order, reserve=False):
    # Кэшируем заголовки один раз!
    if not hasattr(ws, '_cached_header'):
        ws._cached_header = ws.row_values(1)
    header = ws._cached_header
    row_data = [data_dict.get(col, "") for col in column_order]
    all_rows = ws.get_all_values()
    main_start, main_end = 2, len(all_rows)
    if reserve:
        for i, row in enumerate(all_rows):
            if "Команды резерв" in row:
                main_start = i+2
                break
    insert_row = None
    for i in range(main_start-1, main_end):
        if len(all_rows[i]) == 0 or all(cell == "" for cell in all_rows[i]):
            insert_row = i+1
            break
    if not insert_row:
        insert_row = main_end+1
    ws.insert_row(row_data, insert_row)