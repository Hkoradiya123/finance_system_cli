#! • Additional attribute: interest_rate (e.g., 4.5%).
#! • apply_monthly_update(): Add monthly interest to balance. Formula: balance * interest_rate / 12 / 100.
#! Record as a credit transaction with tag 'interest'.
#! • get_account_type() returns 'Savings'.
#! • Override withdraw() to enforce a minimum balance (e.g., Rs. 1000). Call super().withdraw() after the check


from exceptions import InsufficientFundsError
from account import Account
from transaction import Transaction
# from user import User
# import user


class SavingsAccount(Account):

    def __init__(self, user_id, balance: float = 0.0):
        super().__init__( user_id, balance)
        self.account_type = "Savings"
        self.interest_rate = 4.5  
        self.monthly_fee = 200.0
        self.overdraft_limit = 5000.0

    def get_account_type(self) -> str:
        return self.account_type

    # def apply_monthly_update(self):
    #     # Deduct monthly fee from balance
    #     monthly_fee = self.monthly_fee
    #     self.balance -= monthly_fee
    #     self.add_transaction(monthly_fee, "monthly_fee")

    def apply_monthly_update(self):
        monthly_interest = self.balance * self.interest_rate / 12 / 100
        if self.balance > 0:
            self._set_balance(self.balance + monthly_interest)
            transaction = Transaction.create(monthly_interest, "credit", "Monthly interest", tags=["interest"])
            self.history.append(transaction)

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds for this withdrawal.")
        if self.balance - amount < 1000:
            raise InsufficientFundsError("Withdrawal would breach minimum balance of Rs. 1000.")
        super().withdraw(amount)
