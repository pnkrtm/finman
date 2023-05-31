import datetime
from collections import OrderedDict
from typing import Any, Dict

import numpy as np
from splitwise import Category, Expense, Group, Splitwise, User
from splitwise.exception import SplitwiseUnauthorizedException
from splitwise.user import ExpenseUser

from src.finman.exceptions.swise_exceptions import SwiseAuthorizeException
from src.finman.expenses.base import BaseSingleExpense
from src.finman.utils.transaction_types import TransactionType

TRANS_ID = {TransactionType.GROCERY: 12, TransactionType.RESTAURANT: 13, TransactionType.CAFFE: 13}


class SwiseAdapter:
    _swise_obj: Splitwise = None
    _current_user: User = None
    _current_group: Group = None
    _default_shares: Dict[int, float] = None  # group default shares
    _custom_shares: Dict[int, Dict[int, float]] = None  # group custom shares by transaction type

    def authenticate(self, consumer_key, consumer_secret, api_key):
        try:
            self._swise_obj = Splitwise(consumer_key, consumer_secret, api_key=api_key)
            self._current_user = self._swise_obj.getCurrentUser()

        except SplitwiseUnauthorizedException as e:
            raise SwiseAuthorizeException("Problems with Splitwise authentication")

    def send_transaction(self, transaction: BaseSingleExpense):
        if self._current_user is None:
            raise ValueError("Current user is None!")

        if self._current_group is None:
            raise ValueError("Current group is None!")

        swise_expense = self._prepare_transaction(transaction)

        created_expense, errors = self._swise_obj.createExpense(swise_expense)

        if errors is None:
            return True

        return False

    def _prepare_transaction(self, transaction: BaseSingleExpense):
        swise_expense = Expense()

        swise_expense.setDescription(transaction.description)
        swise_expense.setCurrencyCode(transaction.currency)
        swise_expense.setGroupId(self._current_group.getId())

        swise_category = Category()
        category_id = TRANS_ID.get(transaction.category, None)
        swise_category.setId(category_id)
        swise_expense.setCategory(swise_category)
        # weird bug in Splitwise API, need to add 1 more day to date of transaction
        swise_expense.setDate((transaction.date_time + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))

        group_users = self._current_group.getMembers()
        if self._custom_shares is not None and category_id in self._custom_shares:
            user_shares = self._custom_shares[category_id]

        else:
            user_shares = self._default_shares

            if user_shares is None:
                user_shares = {user.getId(): 1 / len(group_users) for user in group_users}

        cumulative_cost = 0
        swise_users = OrderedDict()
        for user in group_users:
            if user.getId() in user_shares:
                swise_users[user.getId()] = ExpenseUser()
                swise_users[user.getId()].setId(user.getId())
                user_cost = np.round(user_shares[user.getId()] * transaction.amount, 2)
                swise_users[user.getId()].setOwedShare(user_cost)
                cumulative_cost += user_cost

        swise_users[self._current_user.getId()].setPaidShare(cumulative_cost)
        swise_expense.setUsers(list(swise_users.values()))
        swise_expense.setCost(cumulative_cost)

        return swise_expense

    def set_current_group(self, group_id: int):
        self._current_group = self._swise_obj.getGroup(group_id)

    def configure(self, config: Dict[Any, Any]):
        def _convert_keys(input_dict: Dict[str, Any]):
            return {int(key): _convert_keys(value) if isinstance(value, dict) else value for key, value in input_dict.items()}

        self._default_shares = config.get("default_shares", None)
        if self._default_shares is not None:
            self._default_shares = _convert_keys(self._default_shares)

        self._custom_shares = config.get("custom_shares", None)
        if self._custom_shares is not None:
            self._custom_shares = _convert_keys(self._custom_shares)
