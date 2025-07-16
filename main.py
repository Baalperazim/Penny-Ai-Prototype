# main.py
from sms_reader import SMSReader
from notifier import Notifier
from penny import BudgetManager
import os

def main():
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    # Step 1: Initialize core modules
    reader = SMSReader()
    notifier = Notifier()
    budget = BudgetManager()

    # Step 2: Read SMS transactions
    transactions = reader.read_sms()

    # Step 3: Feed into budget system
    for tx in transactions:
        budget.add_transaction(tx)

    # Step 4: Save transaction log
    budget.export_transactions()

    # Step 5: Budget breach check
    if budget.is_budget_breached():
        notifier.send_alert("Budget limit exceeded! You are overspending.")
    else:
        print("✅ All good. Budget not yet breached.")

if __name__ == "__main__":
    main()
