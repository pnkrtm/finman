import PyPDF2

from src.finman.exceptions.expense_exceptions import StatementParseException
from src.finman.expenses.bunq import BunqSingleExpense
from src.finman.expenses.revolut import RevolutSingleExpense


def get_expense_object(filename: str):
    with open(filename, "rb") as f:
        text = PyPDF2.PdfReader(f).pages[0].extract_text()

    if "REVOLT21" in text.upper():
        return RevolutSingleExpense()

    elif "BIC: BUNQNL2A" in text.upper():
        return BunqSingleExpense()

    raise StatementParseException("Unknown bank for current statement")
