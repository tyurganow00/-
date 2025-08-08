import signal
import sys
import logging
import time
import email

from config import settings
from imap_utils import connect_imap, fetch_unseen_emails, fetch_email
from spreadsheet_utils import connect_sheets, ensure_id_column
from logging_utils import setup_logging, log_event
from parsers import parse_email

LOGFILE = "booking_processor.log"

def graceful_shutdown(signum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

def main_loop():
    setup_logging(LOGFILE)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    spreadsheet = connect_sheets(settings.google_credentials_file, settings.spreadsheet_id)
    log_sheet = spreadsheet.worksheet("Логи")
    sheet = spreadsheet.worksheet("Заявки")
    ensure_id_column(sheet)
    imap = connect_imap(settings.imap_user, settings.imap_password, settings.imap_server)
    while True:
        try:
            ids = fetch_unseen_emails(imap)
            for num in ids:
                raw = fetch_email(imap, num)
                if not raw:
                    continue
                msg = email.message_from_bytes(raw)
                subject = msg.get('Subject', '')
                body = None
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            break
                else:
                    body = msg.get_payload(decode=True)
                if isinstance(body, bytes):
                    body = body.decode("utf-8", errors="ignore")
                fields = parse_email(body)
                if fields:
                    sheet.append_row([
                        fields.get("theme", ""),
                        fields.get("date_str", ""),
                        fields.get("start_time", ""),
                        fields.get("location", ""),
                        fields.get("Команда", ""),
                        fields.get("Источник", "")
                    ], value_input_option="RAW")
                    status = "обработано"
                else:
                    status = "не распознано"
                log_event(
                    log_sheet,
                    "Заявки",
                    fields or {},
                    status,
                    "",
                    "parser",
                    msg.get("Message-ID", ""),
                    subject,
                    num
                )
            time.sleep(30)
        except Exception as e:
            logging.error(f"Ошибка процесса: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main_loop()