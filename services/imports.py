from typing import Iterable
import pandas as pd
from repos.categories_repo import get_or_create_category, get_category_id_by_name
from repos.transactions_repo import insert_transaction_by_category_id

def import_rows(rows: Iterable[dict], create_missing_categories: bool, default_kind: str = "expense"):

    imported = 0
    for r in rows:
        kind_val = r.get("kind")
        if kind_val is None or pd.isna(kind_val):
            kind = default_kind
        else:
            kind = str(kind_val).strip().lower() or default_kind

        cat_val = r.get("category")
        if cat_val is None or pd.isna(cat_val):
            continue
        cat_name = str(cat_val).strip()
        if not cat_name:
            continue

        amt_val = r.get("amount")
        if amt_val is None or pd.isna(amt_val):
            continue
        try:
            amount = float(amt_val)
        except Exception:
            continue
        if amount <= 0:
            continue

        desc_val = r.get("description")
        desc = "" if desc_val is None or pd.isna(desc_val) else str(desc_val).strip()

        acct_val = r.get("account")
        account = "Cash" if acct_val is None or pd.isna(acct_val) else str(acct_val).strip() or "Cash"

        d = r.get("date")
        if d is None or (isinstance(d, float) and pd.isna(d)):
            continue
        tx_date = pd.to_datetime(d, errors="coerce")
        if pd.isna(tx_date):
            continue
        tx_date = tx_date.date()

        if create_missing_categories:
            cat_id = get_or_create_category(cat_name, kind)
        else:
            cat_id = get_category_id_by_name(cat_name, kind)
            if cat_id is None:
                continue

        insert_transaction_by_category_id(tx_date, desc, amount, int(cat_id), account)
        imported += 1

    return imported
