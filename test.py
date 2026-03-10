import sys
import unittest
from unittest.mock import patch

from account import Account
from accounts.savings import SavingsAccount
from accounts.current import CurrentAccount
from accounts.loan import LoanAccount
from exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    AccountNotFoundError,
)
from user import User
from utils import format_currency
from transaction import Transaction


# ── Account base behaviour ──────────────────────────────────────────────────

class TestValidateAmount(unittest.TestCase):
    def setUp(self):
        self.acc = SavingsAccount("U001", 5000)

    def test_positive_amount_ok(self):
        self.acc.validate_amount(100)   # should not raise

    def test_zero_raises(self):
        with self.assertRaises(InvalidAmountError):
            self.acc.validate_amount(0)

    def test_negative_raises(self):
        with self.assertRaises(InvalidAmountError):
            self.acc.validate_amount(-1)

    def test_non_numeric_raises(self):
        with self.assertRaises(InvalidAmountError):
            self.acc.validate_amount("abc")


class TestAccountEquality(unittest.TestCase):
    def test_same_id_equal(self):
        a = SavingsAccount("U001", 1000)
        b = SavingsAccount("U001", 2000)
        b.account_id = a.account_id  # Force same ID to verify equality is based on account_id
        self.assertEqual(a, b)

    def test_different_id_not_equal(self):
        a = SavingsAccount("U001", 1000)
        b = SavingsAccount("U001", 1000)
        self.assertNotEqual(a, b)

    def test_str_contains_type(self):
        a = SavingsAccount("U001", 1000)
        self.assertIn("Savings", str(a))


class TestDeposit(unittest.TestCase):
    def test_deposit_increases_balance(self):
        acc = SavingsAccount("U001", 1000)
        acc.deposit(500)
        self.assertEqual(acc.balance, 1500)

    def test_deposit_records_transaction(self):
        acc = SavingsAccount("U001", 1000)
        before = len(acc.history)
        acc.deposit(100)
        self.assertEqual(len(acc.history), before + 1)

    def test_deposit_zero_raises(self):
        acc = SavingsAccount("U001", 1000)
        with self.assertRaises(InvalidAmountError):
            acc.deposit(0)

    def test_deposit_negative_raises(self):
        acc = SavingsAccount("U001", 1000)
        with self.assertRaises(InvalidAmountError):
            acc.deposit(-50)


class TestGetSummary(unittest.TestCase):
    def test_summary_fields(self):
        acc = SavingsAccount("U001", 2000)
        summary = acc.get_summary()
        self.assertEqual(summary.account_id, acc.account_id)
        self.assertEqual(summary.account_type, "Savings")
        self.assertEqual(summary.balance, 2000)
        self.assertEqual(summary.total_transactions, 0)


class TestGetStatement(unittest.TestCase):
    def test_all_transactions_returned(self):
        acc = SavingsAccount("U001", 5000)
        acc.deposit(100)
        acc.deposit(200)
        self.assertEqual(len(acc.get_statement()), 2)

    def test_month_filter(self):
        acc = SavingsAccount("U001", 5000)
        # Inject transactions with known timestamps
        t1 = Transaction(100, "credit", "Jan", timestamp="2026-01-15T10:00:00")
        t2 = Transaction(200, "credit", "Mar", timestamp="2026-03-10T10:00:00")
        acc.history.extend([t1, t2])
        jan = acc.get_statement(month=1)
        self.assertEqual(len(jan), 1)
        self.assertEqual(jan[0].amount, 100)


# ── SavingsAccount ──────────────────────────────────────────────────────────

class TestSavingsAccount(unittest.TestCase):
    def test_type(self):
        acc = SavingsAccount("U001", 5000)
        self.assertEqual(acc.get_account_type(), "Savings")

    def test_apply_monthly_update_adds_interest(self):
        acc = SavingsAccount("U001", 12000)
        acc.apply_monthly_update()
        expected = 12000 + 12000 * 4.5 / 12 / 100
        self.assertAlmostEqual(acc.balance, expected, places=5)

    def test_withdraw_minimum_balance_enforced(self):
        acc = SavingsAccount("U001", 1500)
        with self.assertRaises(InsufficientFundsError):
            # would leave only 400, below Rs.1000 minimum
            with patch("builtins.input", return_value=""):
                acc.withdraw(1100)

    def test_withdraw_ok(self):
        acc = SavingsAccount("U001", 5000)
        with patch("builtins.input", return_value="groceries"):
            acc.withdraw(500)
        self.assertEqual(acc.balance, 4500)


# ── CurrentAccount ──────────────────────────────────────────────────────────

class TestCurrentAccount(unittest.TestCase):
    def test_type(self):
        acc = CurrentAccount("U001", 3000)
        self.assertEqual(acc.get_account_type(), "Current")

    def test_monthly_fee_deducted(self):
        acc = CurrentAccount("U001", 3000)
        acc.apply_monthly_update()
        self.assertEqual(acc.balance, 2800)

    def test_overdraft_allowed(self):
        acc = CurrentAccount("U001", 100)
        with patch("builtins.input", return_value="bills"):
            acc.withdraw(500)   # within overdraft limit of 5000
        self.assertEqual(acc.balance, -400)

    def test_overdraft_limit_exceeded_raises(self):
        acc = CurrentAccount("U001", 100)
        with self.assertRaises(InsufficientFundsError):
            with patch("builtins.input", return_value=""):
                acc.withdraw(5200)  # 100 + 5000 limit = 5100 max


# ── LoanAccount ─────────────────────────────────────────────────────────────

class TestLoanAccount(unittest.TestCase):
    def _make_loan(self, principal=12000, months=12):
        linked = SavingsAccount("U001", 50000)
        loan = LoanAccount("U001", principal=principal,
                           remaining_months=months, linkedBankAccount=linked)
        return loan, linked

    def test_initial_balance_negative(self):
        loan, _ = self._make_loan(12000, 12)
        self.assertEqual(loan.balance, -12000)

    def test_type(self):
        loan, _ = self._make_loan()
        self.assertEqual(loan.get_account_type(), "Loan")

    def test_deposit_raises(self):
        loan, _ = self._make_loan()
        with self.assertRaises(Exception):
            loan.deposit(100)

    def test_withdraw_raises(self):
        loan, _ = self._make_loan()
        with self.assertRaises(Exception):
            loan.withdraw(100)

    def test_apply_monthly_update_reduces_linked_balance(self):
        loan, linked = self._make_loan(12000, 12)
        before = linked.balance
        loan.apply_monthly_update()
        self.assertLess(linked.balance, before)


# ── User ─────────────────────────────────────────────────────────────────────

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User("U001", "Alice", "alice@example.com")
        self.savings = SavingsAccount("U001", 3000)
        self.current = CurrentAccount("U001", 2000)
        self.user.add_account(self.savings)
        self.user.add_account(self.current)

    def test_total_balance(self):
        self.assertEqual(self.user.total_balance(), 5000)

    def test_add_duplicate_raises(self):
        with self.assertRaises(ValueError):
            self.user.add_account(self.savings)

    def test_get_account_not_found(self):
        with self.assertRaises(AccountNotFoundError):
            self.user.get_account(999)

    def test_remove_account(self):
        self.user.remove_account(self.savings.account_id)
        with self.assertRaises(AccountNotFoundError):
            self.user.get_account(self.savings.account_id)

    def test_net_worth_with_loan(self):
        linked = self.savings
        loan = LoanAccount("U001", principal=5000,
                           remaining_months=10, linkedBankAccount=linked)
        self.user.add_account(loan)
        # total non-loan balances minus loan outstanding
        self.assertEqual(self.user.net_worth(), 5000 - 5000)

    def test_get_all_summaries(self):
        summaries = self.user.get_all_summaries()
        self.assertEqual(len(summaries), 2)

    def test_apply_all_monthly_updates(self):
        errors = self.user.apply_all_monthly_updates()
        self.assertIsInstance(errors, list)


# ── format_currency ──────────────────────────────────────────────────────────

class TestFormatCurrency(unittest.TestCase):
    def test_small_amount(self):
        self.assertEqual(format_currency(100), "Rs. 100.00")

    def test_thousands(self):
        self.assertEqual(format_currency(1000), "Rs. 1,000.00")

    def test_one_lakh(self):
        self.assertEqual(format_currency(100000), "Rs. 1,00,000.00")

    def test_ten_lakhs(self):
        self.assertEqual(format_currency(1000000), "Rs. 10,00,000.00")

    def test_one_crore(self):
        self.assertEqual(format_currency(10000000), "Rs. 1,00,00,000.00")

    def test_negative(self):
        result = format_currency(-500)
        self.assertIn("-", result)
        self.assertIn("500", result)

    def test_decimal(self):
        self.assertEqual(format_currency(1234.56), "Rs. 1,234.56")


if __name__ == "__main__":
    unittest.main()
