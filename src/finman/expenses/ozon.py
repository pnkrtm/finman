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
    # Регулярное выражение для поиска необходимых данных
    pattern = r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})\n(\d+)\n(.*?)\n([+-]?\s?\d[\d\s]*\.\d{2})"

    # Поиск всех совпадений
    matches = re.findall(pattern, text, re.S)

    # Преобразование списка в DataFrame
    df = pd.DataFrame(matches, columns=["Дата операции", "Документ", "Назначение платежа", "Сумма операции"])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    df["id"] = df["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["id"] = df["id"].apply(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()[-10:])

    # Удаление лишних пробелов и символов
    df["Сумма операции"] = df["Сумма операции"].str.replace(" ", "")
    df["Сумма операции"] = df["Сумма операции"].str.replace("\xa0", "")

    # Приведение суммы к числовому формату
    df["Сумма операции"] = df["Сумма операции"].str.replace(" ", "").str.replace("\u2009", "")
    df["Сумма операции"] = df["Сумма операции"].str.replace(",", "").astype(float)
    df["Назначение платежа"] = df["Назначение платежа"].str.replace("\n", " ")

    df["Время операции"] = df["Дата операции"]
    df["Дата операции"] = df["Дата операции"].dt.date

    return df[["id", "Дата операции", "Время операции", "Сумма операции", "Документ", "Назначение платежа"]]


def extract_total_operations(text):
    # Регулярные выражения для извлечения значений
    pattern_incomes = r"\nИтого зачислений за период: ([\d\s]+\.\d{2}) [₽$€¥]"
    pattern_expenses = r"\nИтого списаний за период: ([\d\s]+\.\d{2}) [₽$€¥]"

    # Поиск совпадений
    incomes = re.search(pattern_incomes, text)
    expenses = re.search(pattern_expenses, text)

    # Результаты
    incomes_value = float(incomes.group(1).replace(' ', '')) if incomes else None
    expenses_value = float(expenses.group(1).replace(' ', '')) if expenses else None

    return incomes_value, expenses_value
