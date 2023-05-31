import json
from typing import Any, Dict

from loguru import logger

from src.finman.exceptions.base import FinManBaseException
from src.finman.exceptions.moneywiz_exception import MoneyWizBaseException
from src.finman.exceptions.swise_exceptions import SwiseBaseException
from src.finman.expenses.base import BaseSingleExpense
from src.finman.expenses.factory import get_expense_object
from src.finman.finapps.money_wiz import MoneyWizAdapter
from src.finman.finapps.swise import SwiseAdapter


def _handle_exceptions(func):
    def inner(*args, **kwargs):
        try:
            return {"success": True, "output": func(*args, **kwargs)}

        except FinManBaseException as e:
            return {"success": False, "reason": f"Internal problems while {func.__doc__}", "message": str(e)}

        except Exception as e:
            logger.opt(exception=e).info("Logging exception traceback")
            return {"success": False, "reason": f"Unknown problems while {func.__doc__}", "message": str(e)}

    return inner


class PipelineMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ProcessPipeline(metaclass=PipelineMeta):
    _swise_adapter: SwiseAdapter = None
    _money_wiz_adapter: MoneyWizAdapter = None
    _current_single_expense: BaseSingleExpense = None

    @_handle_exceptions
    def configure(self, filename: str, file_stream=None):
        """
        Configuration of fin apps
        :param filename:
        :param file_stream:
        :return:
        """
        if file_stream is not None:
            config_file = json.loads(file_stream)

        else:
            with open(filename, "rb") as f:
                config_file = json.load(f)

        # todo: Add config validation
        logger.debug("Configuration swise...")
        self._configure_swise(config_file["splitwise"])
        logger.debug("Configuration MoneyWiz...")
        self._configure_moneywiz(config_file["moneywiz"])

    def _configure_swise(self, swise_config: Dict[str, Any]):
        self._swise_adapter = SwiseAdapter()
        self._swise_adapter.authenticate(swise_config["consumer_key"], swise_config["consumer_secret"], swise_config["api_key"])
        self._swise_adapter.set_current_group(swise_config["group_id"])
        self._swise_adapter.configure(swise_config)

    def _configure_moneywiz(self, moneywiz_config: Dict[str, Any]):
        self._money_wiz_adapter = MoneyWizAdapter()
        self._money_wiz_adapter.configure(moneywiz_config)

    @_handle_exceptions
    def read_statement(self, filename: str):
        """
        Reading statement file
        :param filename:
        :return:
        """
        logger.debug("Reading statement started...")
        self._current_single_expense = get_expense_object(filename)
        self._current_single_expense.parse_statement(filename)
        logger.debug("Reading statement finished!")

    @_handle_exceptions
    def send_expenses(self, use_swise: bool) -> Dict[str, Any]:
        """
        Sending expense to fin apps
        :param use_swise:
        :return:
        """
        logger.debug("Sending expense started...")
        if use_swise:
            logger.debug("Sending expense with Splitwise")
            if self._swise_adapter is None:
                raise SwiseBaseException("Splitwise is not configured")

            self._swise_adapter.send_transaction(self._current_single_expense)

        if self._money_wiz_adapter is None:
            raise MoneyWizBaseException("MoneyWiz is not configured")

        logger.debug("Sending expense successfully finished!")

        return {"moneywiz_url_schema": self._money_wiz_adapter.create_url_schema(self._current_single_expense)}
