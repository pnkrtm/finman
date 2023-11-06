import abc
import datetime
import re

import PyPDF2

from src.finman.utils.transaction_types import TransactionType


class BaseSingleExpense:
    _amount: float = -1
    _description: str = None
    _date_time: datetime.datetime = None
    _currency: str = None
    _category: TransactionType = None

    def parse_statement(self, filename: str):
        """
        Main function to call for processing PDF file
        :param filename: PDF filename
        :return:
        """
        with open(filename, "rb") as f:
            self._extract_data_from_statement(PyPDF2.PdfReader(f))

    @abc.abstractmethod
    def _extract_data_from_statement(self, pdf_reader: PyPDF2.PdfReader):
        pass

    @property
    def amount(self):
        return self._amount

    @property
    def description(self):
        return self._description

    @property
    def date_time(self):
        return self._date_time

    @property
    def currency(self):
        return self._currency

    @property
    def category(self):
        return self._category

    @abc.abstractmethod
    def bank_name(self):
        pass


def parse_category(description: str):
    if re.search("(edeka)|(aldi)|(superissimo)|(rewe)", description, re.IGNORECASE):
        return TransactionType.GROCERY

    return None
