import json
from typing import Any, Dict

from loguru import logger

from src.finman.finapps.money_wiz import MoneyWizAdapter
from src.finman.finapps.swise import SwiseAdapter


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

    def configure(self, filename: str, file_stream=None):
        if file_stream is not None:
            config_file = json.loads(file_stream)

        else:
            with open(filename, "rb") as f:
                config_file = json.load(f)

        # Add config validation

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
