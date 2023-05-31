from datetime import datetime

import PyPDF2

from src.finman.exceptions.expense_exceptions import StatementParseException
from src.finman.expenses.base import BaseSingleExpense, parse_category
from src.finman.utils.currencies import CURRENCY


class RevolutSingleExpense(BaseSingleExpense):
    def _extract_data_from_statement(self, pdf_reader: PyPDF2.PdfReader):
        pdf_text = pdf_reader.pages[0].extract_text().split("\n")

        # doesn't seem too strong
        header_row = [row for row in pdf_text if "date description money out money in" in row.lower()]
        if len(header_row) != 1:
            raise StatementParseException("Problems with determination of header row")

        header_row = header_row[0]
        start_i = pdf_text.index(header_row) + 1

        row_splited = pdf_text[start_i].split()
        trans_date = " ".join(row_splited[0:3])

        self._date_time = datetime.strptime(trans_date, "%b %d, %Y")

        if header_row.split()[-1].lower() == "balance":
            amount_idx = -2

        elif header_row.split()[-1].lower() == "in":
            amount_idx = -1

        else:
            raise StatementParseException("Unexpectable header of the last column in statement file")

        self._currency = CURRENCY[row_splited[amount_idx][0]]
        self._amount = float(row_splited[amount_idx][1:])
        self._description = " ".join(row_splited[3:amount_idx])
        self._category = parse_category(self._description)

    @property
    def bank_name(self):
        return "Revolut"
