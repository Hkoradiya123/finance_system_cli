from collections import namedtuple

from account import Account
from transaction import Transaction
from exceptions import UnauthorizedAccessError
# from  user import User


class LoanAccount(Account):

    def __init__(self, user_id, principal, remaining_months):
        super().__init__(user_id, balance=0)
        self.principal = principal
        self.remaining_months = remaining_months
        self.emi_amount = principal / remaining_months
        self._Account__balance = -principal  # Outstanding balance

    def deposit(self, amount):
        raise UnauthorizedAccessError(
            "Loan accounts do not accept deposits", error_code=1005
        )

    def apply_monthly_update(self):
        if self.remaining_months > 0:
            self._Account__balance += (
                self.emi_amount
            )  # Reduce outstanding (negative means debt)
            self.remaining_months -= 1
            transaction = Transaction.create(
                self.emi_amount, "debit", "EMI payment", tags=["emi"]
            )
            self.history.append(transaction)

    def get_account_type(self) -> str:
        return "Loan"

    def loan_summary(self):
        supersummary = super().get_summary()
        summary = namedtuple(
            "LoanSummary", ["principal", "emi", "months_remaining", "total_remaining"]
        )

        return summary(
            self.principal,
            self.emi_amount,
            self.remaining_months,
            max(0, abs(self.balance))
        )

    def get_summary(self):  
        summary = super().get_summary()
        loan_summary = self.loan_summary()

        LoanSummary = namedtuple('LoanSummary', ['account_id', 'account_type', 'balance', 'total_transactions', 'principal', 'emi', 'months_remaining', 'total_remaining'])
        
        return LoanSummary(
            summary.account_id,
            summary.account_type,
            summary.balance,
            summary.total_transactions,
            loan_summary.principal,
            loan_summary.emi,
            loan_summary.months_remaining,
            loan_summary.total_remaining
        )
