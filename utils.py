import sys


def format_currency(amount):
    symbol = "Rs. "

    if amount < 0:
        symbol =  symbol + "-" 
        amount = abs(amount)
    # Split into integer and decimal parts
    integer_part = str(int(amount))
    if "-" in str(amount): integer_part = integer_part.replace("-", "")
    decimal_part = f"{amount:.2f}".split(".")[1]

    integer_part = str(integer_part)

    # last 3 digits--then groups of 2
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]

        pairs = []
        while remaining:
            pairs.append(remaining[0:2])
            remaining = remaining[3:]

        # # Reverse and join
        # pairs.reverse()

        formatted = ",".join(pairs) + "," + last_three
    result = f"{symbol}{formatted}.{decimal_part}"

    return result


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

    all_transactions.sort(key=lambda x: abs(x.amount), reverse=True)

    report["top_5_transactions"] = [
    {
        "amount": txn.amount,
        "type": txn.type,  
        "description": txn.description,
        "timestamp": txn.timestamp
    }
    for txn in all_transactions[:5]
    if txn.type != "loan"
    ]

    return report


def load_transactions_from_file(filename):
    transactions = []
    try:
        with open(filename, "r") as f:
            # Skip header line
            next(f)
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 5:
                    transaction_id, amount, transaction_type, description, timestamp = parts[:5]

                    # tags is stord in like thi steg1 | tag2 | tag3

                    tags = set(s.strip() for s in parts[5].split("|")) if len(parts) > 5 else set()

                    transactions.append(
                        {
                            "transaction_id": transaction_id,
                            "amount": float(amount),
                            "type": transaction_type,
                            "description": description,
                            "timestamp": timestamp,
                            "tags": tags,
                        }
                    )
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

    return transactions

print("Loading transactions from file...\n")
print(load_transactions_from_file("data\\transactions.csv"))


