#!  Additional attributes: monthly_fee (e.g., Rs. 200) and overdraft_limit (e.g., Rs. 5000).
#! • apply_monthly_update(): Deduct monthly fee. Record as debit with tag 'fee'.
#! • get_account_type() returns 'Current'.
#! • Override withdraw() to allow overdraft up to overdraft_limit. Raise InsufficientFundsError only if overdraft
#! limit is also breached

from account import Account 


from exceptions import *


class CurrentAccount(Account):
    def __init__(self,user_id, balance: float = 0.0):
        super().__init__( user_id, balance)
        self.account_type = 'Current'
        self.interest_rate = 0.0 
        self.monthly_fee = 200.0 
        self.overdraft_limit = 5000.0  

    @property
    def balance(self):
        return self._Account__balance
    
    def get_account_type(self) -> str:
        return 'Current'

    def apply_monthly_update(self):
        self._Account__balance -= self.monthly_fee
        self.add_transaction(self.monthly_fee, "debit", tags="fee")
