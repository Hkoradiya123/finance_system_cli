
#! FinanceException
#! ├── InsufficientFundsError
#! ├── InvalidAmountError
#! ├── AccountNotFoundError
#! └── UnauthorizedAccessError

class FinanceException(Exception):
    pass

class InsufficientFundsError(FinanceException):
    pass


class InvalidAmountError(FinanceException):
    pass


class AccountNotFoundError(FinanceException):
    pass


class UnauthorizedAccessError(FinanceException):
    pass



