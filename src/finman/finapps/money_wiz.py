from typing import Any, Dict

from src.finman.expenses.base import BaseSingleExpense


class MoneyWizAdapter:
    _accounts: Dict[str, Dict[str, str]] = None  # "Bank Name"->"Currency"->"Account Name"

    def create_url_schema(self, transaction: BaseSingleExpense):
        url_schema = f"moneywiz://expense?amount={transaction.amount}"

        description = transaction.description.replace(" ", "%20")
        url_schema += f"&description={description}&payee={description}"

        bank_name = transaction.bank_name
        currency = transaction.currency
        if self._accounts is not None and bank_name in self._accounts and currency in self._accounts[bank_name]:
            url_schema += f"&account={self._accounts[bank_name][currency]}"

        else:
            url_schema += f"&currency={transaction.currency}"

        return url_schema

    def configure(self, config: Dict[str, Any]):
        self._accounts = config.get("accounts", None)
