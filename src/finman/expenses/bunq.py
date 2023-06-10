from datetime import datetime

import PyPDF2

from src.finman.exceptions.expense_exceptions import StatementParseException
from src.finman.expenses.base import BaseSingleExpense, parse_category
from src.finman.utils.currencies import CURRENCY
from typing import List


class BunqSingleExpense(BaseSingleExpense):
    def _extract_data_from_statement(self, pdf_reader: PyPDF2.PdfReader):
        pdf_text = pdf_reader.pages[0].extract_text().split("\n")

        # doesn't seem too strong
        header_row = [row for row in pdf_text if "description amount" in row.lower()]

        if len(header_row) != 1:
            raise StatementParseException("Problems with determination of header row")

        header_row = header_row[0]
        start_i = pdf_text.index(header_row) + 1

        row_splited = pdf_text[start_i].split()
        trans_date = row_splited[0]

        self._date_time = datetime.strptime(trans_date, "%Y-%m-%d")
        amount_idx = -3

        self._currency = CURRENCY[row_splited[-1]]
        self._amount = float("".join(row_splited[amount_idx: -1]).replace(",", "."))

        def _get_description(text_list: List[str]):
            description = []
            for item in text_list:
                if text_list.count(item) == 2 and item not in description:
                    description.append(item)

            return " ".join(description)

        self._description = _get_description(row_splited[2: amount_idx])
        self._category = parse_category(self._description)

    @property
    def bank_name(self):
        return "Bunq"
