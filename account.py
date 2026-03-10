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
# from utils import format_currency 


class Account(abc.ABC):
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

    @balance.setter
    def systemBalance(self, amount):
        self.__balance = amount

    @balance.setter
    def balance(self, amount):
        self.validate_amount(amount)
        self.__balance = amount

    @abc.abstractmethod
    def apply_monthly_update(self):
        pass

    @abc.abstractmethod
    def get_account_type(self) -> str:
        pass

    @staticmethod
    def validate_amount(amount):
        if amount < 0:
            raise InvalidAmountError("Amount must be a positive number.")   

    def deposit(self, amount):
        self.validate_amount(amount)
        self.balance += amount
        transaction = Transaction(amount, 'credit', 'Deposit')
        self.history.append(transaction)

    def withdraw(self, amount):
        self.validate_amount(amount)
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds for this withdrawal.")
        tags =  input("Enter a tag for this withdrawal (e.g., groceries, bills, etc.): ")

        tags = set(s.strip() for s in tags.split(",")) if tags!= "" else ""

        self.balance -= amount
        transaction = Transaction(amount, 'debit', 'Withdrawal', tags=tags) 
        self.history.append(transaction)
    def get_statement(self, month: int = None):
        if month is not None:
            return [t for t in self.history if int(t.timestamp[5:7]) == month]
        return self.history

    def get_summary(self) -> tuple:
        summary = namedtuple('Summary', ['account_id', 'account_type', 'balance', 'total_transactions'])
        return summary(
            self.account_id,
            self.get_account_type(),
            self.balance,
            len(self.history),
        )

    def add_transaction(self, amount: float, transaction_type: str, tags=None):
        transaction = Transaction(amount, transaction_type, tags=tags)
        self.history.append(transaction)    

    def loan_penalty(self,emi_amount, penalty_rate = 0.02):
        self.validate_amount(emi_amount)
        penalty_amount = emi_amount * penalty_rate
        self.validate_amount(penalty_amount)
        self.systemBalance = self.systemBalance - penalty_amount
        transaction = Transaction(penalty_amount, 'debit', 'Loan emi with penalty', tags=['penalty'])
        self.history.append(transaction)

    def loan_monthly_update(self, emi_amount: float, interest_amount: float):
        self.validate_amount(emi_amount)
        self.validate_amount(interest_amount)
        if self.balance < emi_amount:
            self.loan_penalty(emi_amount)
        else:
            self.systemBalance = self.systemBalance - emi_amount
            transaction = Transaction(
                emi_amount,
                'debit',
                'Loan EMI payment',
                tags=['emi']
            )
            self.history.append(transaction)
