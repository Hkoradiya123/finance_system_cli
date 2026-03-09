#! Requirements:
#! • Attributes: user_id, name, email, __accounts (private dict mapping account_id → Account).
#! • add_account(account) — adds to the dict. Raises ValueError if account already exists.
#! • get_account(account_id) — retrieves account. Raises AccountNotFoundError if not found.
#! • remove_account(account_id) — removes account from the dict.
#! • total_balance() — returns the sum of balances across all non-loan accounts.
#! • net_worth() — total_balance() minus sum of all loan outstanding balances.
#! • get_all_summaries() — returns a list of named tuples from get_summary() for every account.
#! • apply_all_monthly_updates() — calls apply_monthly_update() on every account. Do NOT crash on errors
#! — collect exceptions and return them as a list


from collections import namedtuple

from accounts.savings import SavingsAccount
from accounts.current import CurrentAccount
from accounts.loan import LoanAccount
from exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InsufficientFundsError,
    InvalidAmountError,
    AccountNotFoundError,
    UnauthorizedAccessError,
)

class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self._accounts = {}

    def add_account(self, account):
        if account.account_id in self._accounts:
            raise ValueError(f"Account with ID {account.account_id} already exists for this user.")
        self._accounts[account.account_id] = account

    def get_account(self, account_id):
        if account_id not in self._accounts:
            raise AccountNotFoundError(f"Account with ID {account_id} not found for user {self.user_id}")
        return self._accounts[account_id]
    
    def get_all_accounts(self):
        return list(self._accounts.values())

    def remove_account(self, account_id):
        if account_id not in self._accounts:
            raise AccountNotFoundError(f"Account with ID {account_id} not found for user {self.user_id}")
        del self._accounts[account_id]

    def total_balance(self):
        total = 0
        for account in self._accounts.values():
            if not isinstance(account, LoanAccount):
                total += account.balance
        return total

    def net_worth(self):
        total = self.total_balance()
        for account in self._accounts.values():
            if isinstance(account, LoanAccount):
                total -= account._Account__balance
        return total

    def get_all_summaries(self):
        return [account.get_summary() for account in self.get_all_accounts()]

    def apply_all_monthly_updates(self):
        errors = []
        for account in self._accounts.values():
            try:
                account.apply_monthly_update()
            except Exception as e:
                errors.append(str(e))
                print(f"Error applying monthly update for account {account.account_id}: {e}")
        return errors

    def __repr__(self):
        return f"User(id={self.user_id}, name='{self.name}', email='{self.email}', accounts={len(self._accounts)})"

    def __str__(self):
        return f"User(id={self.user_id}, name='{self.name}', email='{self.email}', accounts={len(self._accounts)})"
