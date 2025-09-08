from repos.transactions_repo import (
    sum_expenses_between,
    count_transactions_between,
    insert_transaction,
)

def get_monthly_expenses(start, end) -> float:
    return sum_expenses_between(start, end)

def get_monthly_transaction_count(start, end) -> int:
    return count_transactions_between(start, end)

def add_transaction(tx_date, description, amount, category_name, account) -> None:
    insert_transaction(tx_date, description, amount, category_name, account)
