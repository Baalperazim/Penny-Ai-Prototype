# penny.py

# --------------------------------------------
# PENNY: Your AI Financial Assistant Core Engine
# Author: Caleb (Lead Architect)
# Description: Core classes and architecture for budget tracking
# --------------------------------------------

import json
from datetime import datetime

# ------------------------------
# Class: Transaction
# Purpose: To store structured data from each SMS
# ------------------------------
def update_budget(self, monthly_amount):
    self.budgets["monthly"] = float(monthly_amount)
    self.save_budgets()
    # Reset transactions to zero when budget changes
    self.transactions = []
    self.export_transactions()  # This clears the transactions.json file
class Transaction:
    def __init__(self, amount, trans_type, date, source):
        self.amount = float(amount)
        self.trans_type = trans_type  # 'credit' or 'debit'
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.source = source  # e.g. Bank name or card number

    def to_dict(self):
        return {
            "amount": self.amount,
            "type": self.trans_type,
            "date": self.date.strftime("%Y-%m-%d"),
            "source": self.source
        }


# ------------------------------
# Class: BudgetManager
# Purpose: Handle user budgets, transaction logging, breach detection
# ------------------------------
class BudgetManager:
    def __init__(self, budget_file='budget.json'):
        self.budget_file = budget_file
        self.transactions = []  # list of Transaction objects
        self.budgets = self.load_budgets()

    def load_budgets(self):
        try:
            with open(self.budget_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"monthly": 0.0}  # default budget

    def save_budgets(self):
        with open(self.budget_file, 'w') as f:
            json.dump(self.budgets, f, indent=4)

    def update_budget(self, monthly_amount):
        self.budgets["monthly"] = float(monthly_amount)
        self.save_budgets()

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_monthly_spending(self):
        now = datetime.now()
        return sum(
            t.amount for t in self.transactions
            if t.trans_type == 'debit' and t.date.month == now.month and t.date.year == now.year
        )

    def is_budget_breached(self):
        return self.get_monthly_spending() > self.budgets["monthly"]

    def export_transactions(self, export_file="transactions.json"):
        with open(export_file, 'w') as f:
            json.dump([t.to_dict() for t in self.transactions], f, indent=4)