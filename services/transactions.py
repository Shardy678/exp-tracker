from repos.transactions_repo import (
    sum_expenses_between,
    count_transactions_between,
    insert_transaction,
)

def get_monthly_expenses(start, end, category_ids=None) -> float:
    return sum_expenses_between(start, end, category_ids)

def get_monthly_transaction_count(start, end, category_ids=None) -> int:
    return count_transactions_between(start, end, category_ids)

def add_transaction(tx_date, description, amount, category_name, account) -> None:
    insert_transaction(tx_date, description, amount, category_name, account)
