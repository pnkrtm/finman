import pandas as pd
import re
from datetime import datetime


def parse_operations_with_check(text):
    # Шаблон для извлечения операций, учитывающий знаки перед суммами (включая длинное тире)
    pattern = re.compile(
        r"(?P<description>.+?)\n"  # Описание операции
        r"(?P<operation_date>\d{2}\.\d{2}\.\d{4})\nв\s\d{2}:\d{2}\n"  # Дата операции
        r"(?P<processing_date>\d{2}\.\d{2}\.\d{4})\n"  # Дата обработки
        r"(?P<amount_operation>[+-−–]?\d[\d\xa0]*,\d{2})\s₽\n"  # Сумма в валюте операции с учётом знака
        r"(?P<amount_esp>[+-−–]?\d[\d\xa0]*,\d{2})\s₽"  # Сумма в валюте ЭСП с учётом знака
    )

    operations = []
    for match in pattern.finditer(text):
        description = match.group("description").replace("\xa0", " ")
        operation_date = datetime.strptime(match.group("operation_date"), "%d.%m.%Y")

        # Обработка суммы с учётом длинного тире и замены символов
        amount_operation_str = match.group("amount_operation").replace("\xa0", "").replace(",", ".")
        amount_esp_str = match.group("amount_esp").replace("\xa0", "").replace(",", ".")

        # Замена длинного тире на обычный минус для корректного преобразования
        amount_operation = float(amount_operation_str.replace("−", "-").replace("–", "-"))
        amount_esp = float(amount_esp_str.replace("−", "-").replace("–", "-"))
        currency = "RUB"

        operations.append({
            "Дата операции": operation_date,
            "Описание операции": description,
            "Сумма в валюте операции": amount_operation,
            "Валюта операции": currency,
            "Сумма в валюте ЭСП": amount_esp
        })

    # Преобразование к DataFrame
    df = pd.DataFrame(operations)

    return df


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
