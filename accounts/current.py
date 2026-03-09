
1#!  Additional attributes: monthly_fee (e.g., Rs. 200) and overdraft_limit (e.g., Rs. 5000).
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
            self.systemBalance = self.systemBalance - self.monthly_fee
            transaction = Transaction.create(
                self.monthly_fee, "debit", "Monthly fee", tags=["fee"]
            )
            self.history.append(transaction)
        elif self.balance < self.monthly_fee:
            errors.append("Insufficient funds to cover the monthly fee.")
        return errors
