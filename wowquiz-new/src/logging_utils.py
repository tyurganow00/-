import datetime

def log_event(log_sheet, sheet_title, data_dict, status, comment, source, message_id, subject, email_uid):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        sheet_title,
        status,
        comment,
        source,
        message_id,
        subject,
        str(email_uid),
        str(data_dict)
    ]
    log_sheet.append_row(row)