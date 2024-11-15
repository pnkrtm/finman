import hashlib
import re

import pandas as pd


def parse_operations(text):
    """_summary_

    :param text: _description_
    :type text: _type_
    :return: _description_
    :rtype: _type_
    """
    # Обновляем регулярное выражение для более точного захвата полного описания операции
    transaction_pattern = re.compile(
        r'(\d{2}\.\d{2}\.\d{4})\n(\d{2}:\d{2})\n\d+\n([^\n]+)\n([+\-\d\s,]+)\n([^\n]+(?:\n[^\n]+)?)'
    )

    # Сбор данных транзакций с учетом времени операции
    transactions = []

    for match in transaction_pattern.finditer(text):
        date, time, category, amount, description = match.groups()
        
        # Полное описание категории с описанием операции
        full_category = f"{category}. {description}"
        
        # Объединение даты и времени
        date_time = f"{date} {time}"
        
        # Определение знака суммы: если нет "+", делаем значение отрицательным
        amount_cleaned = re.sub(r'[^\d\-,.]+', '', amount.replace('\xa0', '').replace(',', '.').strip().split("\n")[0])
        amount_value = float(amount_cleaned.replace(" ", ""))
        if not amount.startswith('+'):
            amount_value = -amount_value  # Превращаем в отрицательное значение
        
        # Добавляем запись в массив
        transactions.append([date_time, full_category, amount_value])

    # Создание DataFrame
    df = pd.DataFrame(transactions, columns=["Дата операции", "Описание", "Сумма в валюте счета"])

    # Преобразование "Дата операции" в datetime и "Сумма в валюте счета" в float
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format='%d.%m.%Y %H:%M')
    df["Сумма в валюте счета"] = df["Сумма в валюте счета"].astype(float)

    df["id"] = df["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["id"] = df["id"].apply(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()[-10:])

    df["Время операции"] = df["Дата операции"]
    df["Дата операции"] = df["Дата операции"].dt.date
    df['Описание'] = df['Описание'].str.replace('\n', ' ')

    return df[["id", "Дата операции", "Время операции", "Сумма в валюте счета", "Описание"]]


def extract_total_operations(text):
    """
    Extracts financial data from a given statement string.

    :param text: The statement containing financial data as a string.
    :return: A dictionary with extracted values.
    """
    # Regex pattern to capture the segment of interest
    pattern = r"ВСЕГО ПОПОЛНЕНИЙ\nВСЕГО СПИСАНИЙ\nОСТАТОК НА(.*?)ДАТА ОПЕРАЦИИ"
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        raise ValueError("The specified section could not be found in the statement.")

    # Extract the relevant part and split by newlines
    relevant_data = match.group(1).strip()
    lines = relevant_data.split("\n")

    if len(lines) != 4:
        raise ValueError("Expected exactly 4 lines of data in the section.")

    # Process and convert each line to a float, cleaning up formatting
    def clean_and_convert(value):
        cleaned = value.replace("\xa0", "").replace(",", ".")
        return float(cleaned)

    result = {
        "balance": clean_and_convert(lines[0]),
        "total_incomes": clean_and_convert(lines[1]),
        "total_expenses": clean_and_convert(lines[2]),
        "balance_at": clean_and_convert(lines[3]),
    }

    return result['total_incomes'], result['total_expenses']

