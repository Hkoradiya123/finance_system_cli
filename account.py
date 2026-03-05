'''account.py Requirements:
• Use Python's abc module. Account must be an Abstract Base Class.
• Encapsulation: Store balance as __balance (private). Expose it via a @property.
• Abstract methods (subclasses MUST implement): apply_monthly_update(self) and
get_account_type(self) -> str.
• deposit(amount) — validates amount using validate_amount(), raises InvalidAmountError if invalid,
appends a Transaction to history.
• withdraw(amount) — validates amount, checks balance, raises InsufficientFundsError if balance is
insufficient.
• get_statement(month=None) — returns a filtered list of transactions. If month (1–12) is given, filter by that
month.
• get_summary() -> namedtuple — returns (account_id, account_type, balance, total_transactions) as a
named tuple.
• Class variable _total_accounts = 0 — increment every time a new account is created.
• @staticmethod validate_amount(amount) — raises InvalidAmountError if amount is not a positive
number.
• Implement __str__ and __eq__ (two accounts are equal if they share the same account_id)
'''
import abc
from collections import namedtuple
from transaction import Transaction
# from user import User
from exceptions import InsufficientFundsError, InvalidAmountError, AccountNotFoundError, UnauthorizedAccessError


class Account(abc.ABC,Transaction):
    _total_accounts = 0

    def __init__(self,User_id,balance: float = 0):
        Account._total_accounts += 1
        self.account_id = Account._total_accounts
        self.owner = User_id
        self.__balance = balance
        self.history = []

    @property
    def balance(self):
        return self.__balance

    @abc.abstractmethod
    def apply_monthly_update(self):
        pass

    @abc.abstractmethod
    def get_account_type(self) -> str:
        pass

    @staticmethod
    def validate_amount(amount):
        if amount <= 0:
            raise InvalidAmountError("Amount must be a positive number.")   

    def deposit(self, amount):
        self.validate_amount(amount)
        self.__balance += amount
        transaction = Transaction(amount, 'credit', 'Deposit')
        self.history.append(transaction)

    def withdraw(self, amount):
        self.validate_amount(amount)
        if amount > self.__balance:
            raise InsufficientFundsError("Insufficient funds for this withdrawal.")
        self.__balance -= amount
        transaction = Transaction(amount, 'debit', 'Withdrawal')
        self.history.append(transaction)

    def get_statement(self, month: int, monthend: int=None):
        if monthend is not None:
            return [t for t in self.history if int(t.timestamp[5:7]) >= month and int(t.timestamp[5:7]) <= monthend]
        return [t for t in self.history if int(t.timestamp[5:7]) == month]

    def get_summary(self) -> tuple:
        summary = namedtuple('Summary', ['account_id', 'account_type', 'balance', 'total_transactions'])
        return summary(self.account_id, self.get_account_type(), self.balance, len(self.history)) 

    def add_transaction(self, amount: float, transaction_type: str, tags=None):
        transaction = Transaction(amount, transaction_type, tags=tags)
        self.history.append(transaction)    
