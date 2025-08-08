import pytest
from src.parsers import parse_email

def test_findquiz_parser():
    text = 'Вау квиз "Тема" 12.08.2024 19:00 в Бар'
    result = parse_email(text)
    assert result['theme'] == "Тема"
    assert result['date_str'] == "12.08"
    assert result['start_time'] == "19:00"
    assert result['location'] == "Бар"

def test_wowquiz_parser():
    text = 'Команда "Котики" зарегистрировалась'
    result = parse_email(text)
    assert result['Команда'] == "Котики"
    assert result['Источник'] == "С"