import hashlib
import pandas as pd
import re
from datetime import datetime


def parse_operations(text):
    # Регулярное выражение для извлечения операций
    pattern = re.compile(
        r"(?P<description>.+?)\s"  # Описание операции
        r"(?P<date>\d{2}\.\d{2}\.\d{4})\sв\s(?P<time>\d{2}:\d{2})\s"  # Дата и время операции
        r"\d{2}\.\d{2}\.\d{4}\s"  # Пропуск даты обработки
        r"(?P<card>\d{4})?\s*"  # Карта (если есть)
        r"(?P<amount_operation>[+-−–]?\d[\d\xa0]*,\d{2})\s(?P<currency_operation>[₽$€¥])\s"  # Сумма в валюте операции
        r"(?P<amount_esp>[+-−–]?\d[\d\xa0]*,\d{2})\s(?P<currency_esp>[₽$€¥])",  # Сумма в валюте ЭСП
        re.MULTILINE
    )

    # Функция для очистки чисел
    def parse_amount(amount):
        number = amount.replace("\xa0", "").replace(",", ".").replace("−", "-").replace("–", "-")
        return float(number)

    # Парсим операции
    matches = pattern.finditer(text)

    transactions = []
    for match in matches:
        # Извлечение данных
        description = match.group('description').strip()
        date_time = f"{match.group('date')} {match.group('time')}"
        card = match.group('card').strip() if match.group('card') else None
        operation_amount = parse_amount(match.group('amount_operation'))
        operation_currency = match.group('currency_operation')
        esp_amount = parse_amount(match.group('amount_esp')) 
        esp_currency = match.group('currency_esp')

        transactions.append({
            "Описание операции": description,
            "Время операции": datetime.strptime(date_time, "%d.%m.%Y %H:%M"),
            "Номер карты": card,
            "Сумма в валюте операции": operation_amount,
            "Валюта операции": operation_currency,
            "Сумма операции в валюте карты": esp_amount,
            "Валюта карты": esp_currency,
        })

    # Создаем DataFrame
    df = pd.DataFrame(transactions)

    df["id"] = df["Время операции"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["id"] = df["id"].apply(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()[-10:])
    df['Дата операции'] = df["Время операции"].dt.date

    return df[[
        "id", "Дата операции", "Время операции", "Сумма операции в валюте карты", "Валюта карты",
        "Сумма в валюте операции", "Валюта операции", "Описание операции", "Номер карты"
    ]]


def extract_total_operations(text):
    # Находим блок текста между "Исходящий остаток за" и "Всего расходных операций"
    match = re.search(r'Исходящий остаток за.*?Всего расходных операций', text, re.DOTALL)
    if not match:
        return None, None  # Если не найдено, возвращаем None

    block = match.group()

    # Извлекаем суммы
    totals = re.findall(r'[+-]?\d[\d\xa0,.]* ₽', block)
    if len(totals) >= 2:  # Проверяем, что нашли как минимум две суммы
        incomes = float(totals[-2].replace('₽', '').replace('\xa0', '').replace(',', '.').strip())
        expenses = float(totals[-1].replace('₽', '').replace('\xa0', '').replace(',', '.').strip())
        return incomes, expenses
    return None, None
