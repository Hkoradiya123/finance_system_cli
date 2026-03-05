import sys
import os
from user import User
from accounts.savings import SavingsAccount
from accounts.current import CurrentAccount
from accounts.loan import LoanAccount
from exceptions import (
    FinanceException,
    InvalidAmountError,
    InsufficientFundsError,
    AccountNotFoundError,
    UnauthorizedAccessError,
)
from utils import format_currency, generate_report, load_transactions_from_file

def wait_for_enter():
    input("Press Enter to continue...")
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def clear_wait(func):
    def wrapper(*args, **kwargs):
        clear_screen()
        result = func(*args, **kwargs)
        wait_for_enter()
        clear_screen()
        return result
    return wrapper


def print_menu():
    print("\n" + "=" * 50)
    print("Personal Finance Management System")
    print("=" * 50)
    print("1. View all accounts")
    print("2. Deposit to account")
    print("3. Withdraw from account")
    print("4. View account statement")
    print("5. Apply monthly updates to all accounts")
    print("6. View full financial report")
    print("7. Exit")
    print("=" * 50)

@clear_wait
def view_all_accounts(user):
    summaries = user.get_all_summaries()
    # for summary in xxyz:
    #     print(summary)
    if not summaries:
        print("No accounts found.")
        return

    print("\n" + "-" * 50)
    print("All Accounts")
    print("-" * 50)
    for summary in summaries:
        account = user.get_account(summary.account_id)
        print(f"ID: {summary.account_id}")
        print(f"  Type: {summary.account_type}")
        print(f"  Balance: {format_currency(summary.balance)}")
        print(f"  Transactions: {summary.total_transactions}")
        if summary.account_type == "Loan" and hasattr(account, "loan_summary"):
            loan_info = account.loan_summary()
            print(f"  Principal: {format_currency(loan_info['principal'])}")
            print(f"  EMI: {format_currency(loan_info['emi'])}")
            print(f"  Months Remaining: {loan_info['months_remaining']}")
        print()
    input("Press Enter to continue...")

@clear_wait
def deposit_to_account(user):
    try:
        account_id = input("Enter account ID: ").strip()
        amount = float(input("Enter amount to deposit: "))

        account = user.get_account(account_id)
        account.deposit(amount)
        print(
            f"Successfully deposited {format_currency(amount)} to account {account_id}"
        )
        print(f"New balance: {format_currency(account.balance)}")
    except ValueError:
        print("Error: Invalid input. Please enter a valid amount.")
    except FinanceException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@clear_wait
def withdraw_from_account(user):
    try:
        account_id = input("Enter account ID: ").strip()
        amount = float(input("Enter amount to withdraw: "))

        account = user.get_account(account_id)
        account.withdraw(amount)
        print(
            f"Successfully withdrew {format_currency(amount)} from account {account_id}"
        )
        print(f"New balance: {format_currency(account.balance)}")
    except ValueError:
        print("Error: Invalid input. Please enter a valid amount.")
    except FinanceException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@clear_wait
def view_statement(user):
    try:
        account_id = input("Enter account ID: ").strip()
        month_input = input(
            "Enter month (1-12) or press Enter to see all transactions: "
        ).strip()

        account = user.get_account(account_id)
        month = None
        if month_input:
            month = int(month_input)
            if month < 1 or month > 12:
                print("Error: Month must be between 1 and 12")
                return

        transactions = account.get_statement(month)
        if not transactions:
            print("No transactions found.")
            return

        print("\n" + "-" * 50)
        print(f"Statement for {account_id} (Month: {month if month else 'All'})")
        print("-" * 50)
        for txn in transactions:
            print(f"  {txn}")
        print("-" * 50)
        print(f"Total Transactions: {len(transactions)}")
    except ValueError:
        print("Error: Invalid input.")
    except FinanceException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@clear_wait
def apply_monthly_updates(user):
    print("\nApplying monthly updates to all accounts...")
    errors = user.apply_all_monthly_updates()

    if errors:
        print(f"Completed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
    else:
        print("All monthly updates applied successfully!")

    # Show updated balances
    print("\nUpdated Account Balances:")
    for summary in user.get_all_summaries():
        account = user.get_account(summary.account_id)
        print(f"  {summary.account_id}: {format_currency(account.balance)}")

@clear_wait
def view_financial_report(user):
    report = generate_report(user)

    print("\n" + "=" * 50)
    print("Financial Report")
    print("=" * 50)
    print(f"User: {report['user']['name']} ({report['user']['user_id']})")
    print(f"Email: {report['user']['email']}")
    print()
    print(f"Total Balance: {format_currency(report['total_balance'])}")
    print(f"Net Worth: {format_currency(report['net_worth'])}")
    print()
    print("-" * 50)
    print("Account Summaries:")
    print("-" * 50)
    for summary in report["account_summaries"]:
        print(
            f"  {summary['account_id']} ({summary['account_type']}): {format_currency(summary['balance'])}"
        )

    print()
    print("-" * 50)
    print("Top 5 Transactions by Amount:")
    print("-" * 50)
    for i, txn in enumerate(report["top_5_transactions"], 1):
        print(
            f"  {i}. {txn['description']}: {format_currency(txn['amount'])} ({txn['type']})"
        )


def main():
    # Create demo user and accounts
    print("Let's set up your account!\n")
    name = input("Enter your name: ").strip()
    email = input("Enter your email: ").strip()
    user = User("U001", name, email)

    print(f"\nWelcome, {user.name}! Your user ID is {user.user_id}. Let's create some accounts for you.")

    print("\nCreating accounts...")

    savingsamount = float(input("Enter initial balance for Savings Account: ").strip())
    currentamount = float(input("Enter initial balance for Current Account: ").strip())

    loadamount = float(input("Enter principal amount for Loan Account: ").strip())
    loanmonths = int(input("Enter remaining months for Loan Account: ").strip())

    savings = SavingsAccount(
        user.user_id,savingsamount
    )
    current = CurrentAccount(
        user.user_id,balance=currentamount
    )
    loan = LoanAccount(
        user.user_id, principal=loadamount, remaining_months=loanmonths
    )

    user.add_account(savings)
    user.add_account(current)
    user.add_account(loan)

    print("Accounts created successfully!\n")
    print(f"your saving account number is \t{savings.account_id}")
    print(f"your current account number is \t{current.account_id}")
    print(f"your loan account number is \t{loan.account_id}\n")
    
    # Display all accounts
    print("All accounts:")
    for account in user.get_all_accounts():
        print(f"  Account ID: {account.account_id}, Type: {type(account).__name__}, Balance: {account.balance}")
    
    wait_for_enter()

    while True:
        try:
            print("Welcome to Personal Finance Management System")
            print(f"User: {user.name} ({user.user_id})")
            print_menu()
            choice = input("Enter your choice (1-7): ").strip()

            if choice == "1":
                view_all_accounts(user)
            elif choice == "2":
                deposit_to_account(user)
            elif choice == "3":
                withdraw_from_account(user)
            elif choice == "4":
                view_statement(user)
            elif choice == "5":
                apply_monthly_updates(user)
            elif choice == "6":
                view_financial_report(user)
            elif choice == "7":
                print("Thank you for using Personal Finance Management System. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        # except Exception as e:
        #     print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
