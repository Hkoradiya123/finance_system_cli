#! Requirements:
#! • Attributes: transaction_id, amount, type ('credit' or 'debit'), description, timestamp, tags (a set).
#! • @staticmethod from_string(data: str) — parses a comma-separated string like
#! "500,credit,salary,tag1|tag2" and returns a Transaction object. This simulates loading data from a
#! CSV file.
#! • @classmethod create(amount, type, description, tags=[]) — auto-generates a transaction_id using a
#! class-level counter and sets the timestamp automatically.
#! • Implement __str__ and __repr__ dunder methods.
#! • Implement to_dict() that returns a dictionary representation of the transaction.


import datetime

class Transaction:
    transaction_counter = 0
    filename = "./data/transactions.csv"
    def __init__(self, amount: float = 0, type: str = None, description:str="", tags: set = None):
        self.transaction_id = self.generate_transaction_id()
        self.amount = amount
        self.type = type  # 'credit' or 'debit'
        self.description = description
        self.timestamp = datetime.datetime.now().isoformat()[0:19]
        self.tags = tags or set()
        self.add_record_to_csv(self.filename)

    def generate_transaction_id(self):
        Transaction.transaction_counter += 1
        return Transaction.transaction_counter

    def add_record_to_csv(self, filename: str):
        with open(filename, 'a') as file:
            file.write(f"{self.transaction_id},{self.amount},{self.type},{self.description},{self.timestamp},{'|'.join(self.tags)}\n")

    def __str__(self):
        return f"Transaction(id={self.transaction_id}, amount={self.amount}, type='{self.type}', description='{self.description}', timestamp='{self.timestamp}', tags={self.tags})"

    def __repr__(self):
        return f"Transaction(id={self.transaction_id}, amount={self.amount}, type='{self.type}', description='{self.description}', timestamp='{self.timestamp}', tags={self.tags})"

    def to_dict(self):
        return {
            'id': self.transaction_id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description, 
            'timestamp': self.timestamp, 
            'tags': self.tags
        }


# * 2026-01-15T10:30:00

# abc = Transaction(500, 'credit', 'salary', {'tag1', 'tag2'})
# print(abc)
