from collections import namedtuple

from account import Account
from transaction import Transaction
from exceptions import UnauthorizedAccessError


class LoanAccount(Account):

    def __init__(
            self, user_id, 
            principal, 
            remaining_months,
            linkedBankAccount
        ):
        super().__init__(user_id, balance=0)
        self.principal = principal
        self.linkedBankAccount = linkedBankAccount
        self.remaining_months = remaining_months
        self.emi_amount = principal / remaining_months
        self.interest_rate = 7.0
        self.systemBalance = -principal  # Outstanding balance

    def deposit(self, amount):
        raise UnauthorizedAccessError("Cannot deposit to a loan account.")

    def withdraw(self, amount):
        raise UnauthorizedAccessError("Cannot withdraw from a loan account.")

    def apply_monthly_update(self):
        errrors = []
        if self.remaining_months > 0:
            if self.linkedBankAccount:
                try:
                    interest = self.principal * self.interest_rate / 100 / 12
                    interest_amount = self.emi_amount + interest
                    self.linkedBankAccount.loan_monthly_update(
                        self.emi_amount, interest_amount
                    )
                    self.remaining_months -= 1
                    self.systemBalance += self.emi_amount
                    transaction = Transaction.create(
                        self.emi_amount, "loan", "EMI payment", tags=["emi"]
                    )
                    self.history.append(transaction)

                except Exception as e:
                    errrors.append(f"EMI payment failed: {str(e)}")
                    # print(f"EMI payment failed: {str(e)}")
                    # input("Press Enter to continue...")
            else:
                errrors.append("No linked EMI account for automatic deduction.")
                # print("No linked EMI account for automatic deduction.")
        else:
            errrors.append("Loan already fully paid.") 
        return errrors

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
            loan_summary.total_remaining,
        )
