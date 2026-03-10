#!  Additional attributes: monthly_fee (e.g., Rs. 200) and overdraft_limit (e.g., Rs. 5000).
#! • apply_monthly_update(): Deduct monthly fee. Record as debit with tag 'fee'.
#! • get_account_type() returns 'Current'.
#! • Override withdraw() to allow overdraft up to overdraft_limit. Raise InsufficientFundsError only if overdraft
#! limit is also breached

from account import Account 


from exceptions import *
from transaction import Transaction


class CurrentAccount(Account):
    def __init__(self,user_id, balance: float = 0.0):
        super().__init__( user_id, balance)
        self.account_type = 'Current'
        self.interest_rate = 0.0 
        self.monthly_fee = 200.0 
        self.overdraft_limit = 5000.0 
    
    def get_account_type(self) -> str:
        return 'Current'

    def apply_monthly_update(self):
        errors = []
        if self.balance >= self.monthly_fee:
            self._set_balance(self.balance - self.monthly_fee)
            transaction = Transaction.create(
                self.monthly_fee, "debit", "Monthly fee", tags=["fee"]
            )
            self.history.append(transaction)
        elif self.balance < self.monthly_fee:
            errors.append("Insufficient funds to cover the monthly fee.")
        return errors

    def withdraw(self, amount):
        self.validate_amount(amount)

        if amount > self.balance + self.overdraft_limit:
            raise InsufficientFundsError(
                f"Overdraft limit exceeded. Available: Rs. {self.balance + self.overdraft_limit}"
            )

        tags = input("Enter a tag for this withdrawal (e.g., groceries, bills, etc.): ")
        tags = set(s.strip() for s in tags.split(",")) if tags != "" else set()

        self._set_balance(self.balance - amount)
        transaction = Transaction(amount, "debit", "Withdrawal", tags=tags)
        self.history.append(transaction)
