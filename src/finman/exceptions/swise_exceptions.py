from src.finman.exceptions.base import FinManBaseException


class SwiseBaseException(FinManBaseException):
    """Base Exception for handling Splitwise actions"""


class SwiseAuthorizeException(SwiseBaseException):
    """Exception for failing swise Authorization"""
