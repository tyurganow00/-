import signal
import sys
import logging
import time
import email

from config import settings
from imap_utils import connect_imap, fetch_unseen_emails, fetch_email
from spreadsheet_utils import connect_sheets, get_or_create_log_worksheet, find_game_worksheet, append_row_by_order
from logging_utils import log_event
from parsers import parse_email

COLUMN_ORDER = [
    "Источник", "Команда", "Кол-во зарегистрировано", "Подтверждено", "Факт (пришло)",
    "№ Стола", "Оплата", "Имя", "Номер", "Email", "Коммент", "ДР", "Готовы принять"
]

def graceful_shutdown(signum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

def is_duplicate(ws, team, phone):
    rows = ws.get_all_values()
    team_lower = (team or "").strip().lower()
    phone_digits = "".join(filter(str.isdigit, phone or ""))
    for row in rows:
        if team_lower and len(row) > 1 and (row[1].strip().lower() == team_lower):
            return True
        if phone_digits and len(row) > 8 and (phone_digits in "".join(filter(str.isdigit, row[8]))):
            return True
    return False

def main_loop():
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    spreadsheet = connect_sheets(settings.google_credentials_file, settings.spreadsheet_id)
    log_sheet = get_or_create_log_worksheet(spreadsheet)
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
                parsed = parse_email(body)
                status = "Ошибка"
                comment = ""
                ws = None
                if parsed:
                    ws = find_game_worksheet(
                        spreadsheet, parsed.theme, parsed.date_str, parsed.location, parsed.start_time
                    )
                    if ws:
                        if is_duplicate(ws, parsed.team, parsed.phone):
                            status = "Дубликат или нет места"
                            comment = "Уже есть такая команда или номер"
                        else:
                            append_row_by_order(ws, parsed.__dict__, COLUMN_ORDER, reserve=parsed.reserve)
                            status = "Добавлено"
                            comment = ""
                    else:
                        status = "Нет листа"
                        comment = f"Нет подходящего листа для {parsed.theme}, {parsed.date_str}, {parsed.location}"
                else:
                    status = "Не распознано"
                    comment = "Письмо не распознано парсером"
                log_event(
                    log_sheet,
                    ws.title if parsed and ws else "",
                    parsed.__dict__ if parsed else {},
                    status,
                    comment,
                    "parser",
                    msg.get("Message-ID", ""),
                    subject,
                    num
                )
                time.sleep(2)  # <------ ЗАДЕРЖКА для Google Sheets API
            time.sleep(settings.check_interval)
        except Exception as e:
            logging.error(f"Ошибка процесса: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main_loop()