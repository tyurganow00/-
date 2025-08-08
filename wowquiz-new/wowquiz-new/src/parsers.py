import re
import dateparser

class BaseParser:
    def parse(self, text: str):
        raise NotImplementedError

class FindQuizParser(BaseParser):
    def parse(self, text: str):
        m = re.search(r'Вау\s*квиз\s*["«](.+?)["»]\s*(\d{2}[-\.]\d{2}[-\.]\d{4})\s*(\d{1,2}:\d{2})\s*в\s*(.+)', text, re.IGNORECASE)
        if m:
            return {
                "theme": m.group(1).strip(),
                "date_str": dateparser.parse(m.group(2), languages=["ru"]).strftime("%d.%m") if m.group(2) else "",
                "start_time": m.group(3).strip(),
                "location": m.group(4).splitlines()[0].strip(),
                "Источник": "Ф"
            }
        return None

class WowQuizParser(BaseParser):
    def parse(self, text: str):
        m = re.search(r'Команда\s+["«](.+?)["»]\s+зарегистрировалась', text)
        if m:
            return {"Команда": m.group(1).strip(), "Источник": "С"}
        return None

def parse_email(text: str):
    parsers = [FindQuizParser(), WowQuizParser()]
    for parser in parsers:
        fields = parser.parse(text)
        if fields:
            return fields
    return None