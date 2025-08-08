import re
from datetime import datetime

class ParsedEmail:
    def __init__(self, theme="", date_str="", location="", start_time="", team="", reserve=False, phone="", email="", name="", comment=""):
        self.theme = theme
        self.date_str = date_str
        self.location = location
        self.start_time = start_time
        self.team = team
        self.reserve = reserve
        self.phone = phone
        self.email = email
        self.name = name
        self.comment = comment

def parse_email(text):
    theme = ""
    date_str = ""
    location = ""
    start_time = ""
    team = ""
    reserve = False
    phone = ""
    email = ""
    name = ""
    comment = ""

    m = re.search(r'Тема[:\s]+(.+)', text)
    if m:
        theme = m.group(1).strip()
    m = re.search(r'Дата[:\s]+([\d\.]+)', text)
    if m:
        date_str = m.group(1).strip()
    m = re.search(r'Площадка[:\s]+(.+)', text)
    if m:
        location = m.group(1).strip()
    m = re.search(r'Время[:\s]+([\d:]+)', text)
    if m:
        start_time = m.group(1).strip()
    m = re.search(r'Команда[:\s]+(.+)', text)
    if m:
        team = m.group(1).strip()
    reserve = "резерв" in text.lower()
    m = re.search(r'Телефон[:\s]+([\d\-\+\(\) ]+)', text)
    if m:
        phone = m.group(1).strip()
    m = re.search(r'Email[:\s]+([\w\.\-@]+)', text)
    if m:
        email = m.group(1).strip()
    m = re.search(r'Имя[:\s]+(.+)', text)
    if m:
        name = m.group(1).strip()
    m = re.search(r'Комментарий[:\s]+(.+)', text)
    if m:
        comment = m.group(1).strip()

    if any([theme, date_str, location, team, phone, email]):
        return ParsedEmail(theme, date_str, location, start_time, team, reserve, phone, email, name, comment)
    return None