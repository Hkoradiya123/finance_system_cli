import sys


def format_currency(amount):
    symbol = "Rs."
    return f"{symbol}{amount:,.2f}"


def generate_report(user):
    report = {
        "user": {
            "name": user.name,
            "user_id": user.user_id,
            "email": user.email,
        },
        "total_balance": 0,
        "net_worth": 0,
        "account_summaries": [],
        "top_5_transactions": [],
    }

    all_transactions = []
    for account in user.get_all_accounts():
        summary = account.get_summary()
        report["account_summaries"].append(summary)
        report["total_balance"] += summary.balance
        report["net_worth"] += summary.balance

        transactions = account.get_statement()
        all_transactions.extend(transactions)

    # Sort transactions by amount (descending) and get top 5
    all_transactions.sort(key=lambda x: abs(x.amount), reverse=True)
    report["top_5_transactions"] = all_transactions[:5]

    return report


def load_transactions_from_file(filename):
    transactions = []
    try:
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    description, amount, transaction_type, account_id = parts
                    transactions.append(
                        {
                            "description": description,
                            "amount": float(amount),
                            "type": transaction_type,
                            "account_id": account_id,
                        }
                    )
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

    return transactions