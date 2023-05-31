import PyPDF2

from src.finman.exceptions.expense_exceptions import StatementParseException
from src.finman.expenses.revolut import RevolutSingleExpense


def get_expense_object(filename: str):
    with open(filename, "rb") as f:
        text = PyPDF2.PdfReader(f).pages[0].extract_text().split("\n")

    if "Revolut Bank UAB" in text[2]:
        return RevolutSingleExpense()

    raise StatementParseException("Unknown bank for current statement")
