import PyPDF2
from datetime import datetime

from src.finman.expenses.base import BaseSingleExpense
from src.finman.utils.currencies import CURRENCY


class RevolutSingleExpense(BaseSingleExpense):
    def _extract_data_from_statement(self, pdf_reader: PyPDF2.PdfReader):
        pdf_text = pdf_reader.pages[0].extract_text().split('\n')

        # doesn't seem too strong
        start_i = pdf_text.index([row for row in pdf_text if row.lower().startswith("start date description")][0]) + 1
        row_splited = pdf_text[start_i].split()
        trans_date = " ".join(row_splited[0: 3])

        self._date_time = datetime.strptime(trans_date, '%b %d, %Y')
        self._currency = CURRENCY[row_splited[-1][0]]
        self._amount = float(row_splited[-1][1:])
        self._description = " ".join(row_splited[3: -1])




