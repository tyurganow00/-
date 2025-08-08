import logging
from logging.handlers import RotatingFileHandler

def setup_logging(logfile: str):
    handler = RotatingFileHandler(logfile, maxBytes=5*1024*1024, backupCount=3)
    logging.basicConfig(level=logging.INFO, handlers=[handler], format="%(asctime)s %(levelname)s %(message)s")

def log_event(log_sheet, sheet_title, fields, status, comment="", parser_type="unknown", message_id="", email_subject="", email_num=""):
    short_comment = (comment[:120] + '...') if len(comment) > 120 else comment
    row = [
        sheet_title or "",
        fields.get("Команда", "") if fields else "",
        status,
        f"{parser_type}; {short_comment}",
        message_id,
        email_subject[:80] if email_subject else "",
        str(email_num)
    ]
    try:
        log_sheet.append_row(row, value_input_option="RAW")
    except Exception as e:
        logging.error(f"Ошибка записи в лог: {e}, row={row}")