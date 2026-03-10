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
import user
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
        # print(summary)
        account = user.get_account(summary.account_id)
        print(f"ID: {summary.account_id}")
        print(f"  Type: {summary.account_type}")
        print(f"  Balance: {format_currency(summary.balance)}")
        print(f"  Transactions: {summary.total_transactions}")
        if summary.account_type == "Loan":
            print(f"  Principal: {format_currency(summary.principal)}")
            print(f"  EMI: {format_currency(summary.emi)}")
            print(f"  Months Remaining: {summary.months_remaining}")
            print(f"  Total Remaining: {format_currency(summary.total_remaining)}")
        print()

@clear_wait
def deposit_to_account(user:User):
    try:
        account_id = int(input("Enter account ID: ").strip())
        amount = float(input("Enter amount to deposit: "))

        account = user.get_account(account_id)
        if isinstance(account, LoanAccount):
            print("\nError: Cannot deposit to a Loan Account.")
            return
        account.deposit(amount)
        print(f"\nSuccessfully deposited {format_currency(amount)} to account {account_id}")
        print(f"New balance: {format_currency(account.balance)}")
    except ValueError:
        print("\nError: Invalid input. Please enter a valid amount.")
    except FinanceException as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

@clear_wait
def withdraw_from_account(user:User):
    try:
        account_id = int(input("Enter account ID: ").strip())
        amount = float(input("Enter amount to withdraw: "))

        account = user.get_account(account_id)
        account.withdraw(amount)
        print(f"\nSuccessfully withdrew {format_currency(amount)} from account {account_id}")
        print(f"New balance: {format_currency(account.balance)}")
    except ValueError:
        print("\nError: Invalid input. Please enter a valid amount.")
    except InsufficientFundsError as e:
        print(f"\nError: {e}")
    except FinanceException as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

@clear_wait
def view_statement(user:User):
    try:
        account_id = int(input("Enter account ID: ").strip())
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
            print("\nNo transactions found.")
            return

        print("\n" + "-" * 50)
        print(f"Statement for account no : {account_id} (Month: {month if month else 'All'})")
        for txn in transactions:
            print("-" * 50)
            txn = txn.to_dict()
            print(f"  id : {txn['id']}")
            print(f"  amount : {txn['amount']}")
            print(f"  type : {txn['type']}")
            print(f"  description : {txn['description']}")
            print(f"  tags : {txn['tags']}")
        print("-" * 50)
        print(f"\nTotal Transactions: {len(transactions)}")
    except ValueError:
        print("\nError: Invalid input.")
    except FinanceException as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

@clear_wait
def apply_monthly_updates(user:User):
    print("\nApplying monthly updates to all accounts...")
    # user.apply_all_monthly_updates()
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
def view_financial_report(user:User):
    try:
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
        
        if report.get("account_summaries"):
            for summary in report["account_summaries"]:
                print(
                    f"  {summary.account_id} ({summary.account_type}): {format_currency(summary.balance)}"
                )
        else:
            print("  No accounts found.")

        print()
        print("-" * 50)
        print("Top 5 Transactions by Amount:")
        print("-" * 50)
        
        if report.get("top_5_transactions") and len(report["top_5_transactions"]) > 0:
            for i, txn in enumerate(report["top_5_transactions"], 1):
                print(
                    f"  {i}. {txn.get('description', 'N/A')}: {format_currency(txn.get('amount', 0))} ({txn.get('type', 'N/A')})"
                )
        else:
            print("  No transactions found.")
            
    except KeyError as e:
        print(f"\nError: Missing data in report - {e}")
        print("Please ensure all accounts have transactions.")
    except TypeError as e:
        print(f"\nError: Data format issue - {e}")
    except Exception as e:
        print(f"\nUnexpected error generating report: {e}")


@clear_wait
def setup_user():

    global user

    print("Let's set up your account!")
    print()
    name = input("Enter your name: ").strip()
    email = input("Enter your email: ").strip()
    user = User("U001", name, email)

    print(f"\nWelcome, {user.name}! Your user ID is {user.user_id}. Let's create some accounts for you.")

    print("\nCreating accounts...")
    global savings
    global current

    print()
    savingsamount = float(input("Enter initial balance for Savings Account: ").strip())
    savings = SavingsAccount(user.user_id, savingsamount)
    savings.setAccountPin()

    print()
    currentamount = float(input("Enter initial balance for Current Account: ").strip())
    current = CurrentAccount(user.user_id, balance=currentamount)
    current.setAccountPin()

    user.add_account(savings)
    user.add_account(current)

    loan_choice = input("\nDo you want to set up a loan account? (y/n): ").strip().lower()
    if loan_choice == "y" or loan_choice == "Y":
        print("\nSetting up loan account...")
        print()
        loadamount = float(input("Enter principal amount for Loan Account: ").strip())
        loanmonths = int(input("Enter remaining months for Loan Account: ").strip())

        linkedBankAccount = None
        while not linkedBankAccount:
            try:
                print("\nAll accounts:")
                for account in user.get_all_accounts():
                    print(
                        f"  Account ID: {account.account_id}, Type: {type(account).__name__}, Balance: {format_currency(account.balance)}"
                    )
                print()
                emi_account_choice = int(
                    input(
                        "Which account would you like to use for EMI deductions? (enter account number): "
                    ).strip()
                )
                emi_account = user.get_account(
                    emi_account_choice
                )  # validates ID exists

                if isinstance(emi_account, LoanAccount):
                    print("\nLoan account cannot be used for EMI deduction. Choose Savings/Current.")
                    continue

                linkedBankAccount = emi_account
                break
            except ValueError:
                print("\nPlease enter a valid numeric account number.")
            except AccountNotFoundError:
                print("\nInvalid account number. Try again.")

        loan = LoanAccount(
            user.user_id,
            principal=loadamount,
            remaining_months=loanmonths,
            linkedBankAccount=emi_account,
        )
        user.add_account(loan)

    print("\nAll Accounts created successfully!")
    print()
    print("All accounts:")
    for account in user.get_all_accounts():
        print(
            f"  Account ID: {account.account_id}, Type: {type(account).__name__}, Balance: {format_currency(account.balance)}"
        )

def main():
    clear_screen()
    # Create user and accounts
    # setup_user()

    # ask user to where user want to deduct emi from current or savings account
    while True:
        try:
            setup_user()
            break
        except Exception as e:
            print(f"\nError during setup: {e}")
            retry = input("\nDo you want to try setting up again? (y/n): ").strip().lower()
            if retry == "n" or retry == "N":
                print("\nThank you for using Personal Finance Management System. Goodbye!")
                sys.exit(0)
        except KeyboardInterrupt as e:
            print("\nThank you for using Personal Finance Management System. Goodbye!")
            sys.exit(0)

    while True:
        try:
            clear_screen()
            print("\nWelcome to Personal Finance Management System")
            print(f"User: {user.name} ({user.user_id})")
            print_menu()
            choice = input("\nEnter your choice (1-7): ").strip()

            choice_actions = {
                "1": lambda: view_all_accounts(user),
                "2": lambda: deposit_to_account(user),
                "3": lambda: withdraw_from_account(user),
                "4": lambda: view_statement(user),
                "5": lambda: apply_monthly_updates(user),
                "6": lambda: view_financial_report(user),
            }
            
            # uses dynamic menu handling to avoid long if-elif chains and allow easy extension of features in future
            if choice == str(int(list(choice_actions.keys())[-1]) + 1):
                print("\nThank you for using Personal Finance Management System. Goodbye!")
                break
            elif choice in choice_actions:
                choice_actions[choice]()
            else:
                print("\nInvalid choice. Please enter a number between 1 and 7.")
        except KeyboardInterrupt:
            print("\nThank you for using Personal Finance Management System. Goodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
