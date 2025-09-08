import pandas as pd
import streamlit as st
from services.imports import import_rows
from data.dataframe import load_df  

REQUIRED_FIELDS = ["date", "amount", "category"]
OPTIONAL_FIELDS = ["description", "account", "kind"]

DEFAULT_MAPPING = {
    "date": ["date", "tx_date", "transaction_date"],
    "description": ["description", "desc", "details"],
    "amount": ["amount", "value", "amt"],
    "category": ["category", "cat"],
    "account": ["account", "wallet"],
    "kind": ["type", "kind"],
}

def _deduce_mapping(df: pd.DataFrame) -> dict:
    mapping = {}
    cols_lower = {c.lower(): c for c in df.columns}
    for target, candidates in DEFAULT_MAPPING.items():
        for cand in candidates:
            if cand in cols_lower:
                mapping[target] = cols_lower[cand]
                break
    return mapping

def _parse_file(upload) -> pd.DataFrame | None:
    name = upload.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(upload)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(upload)
    st.error("Unsupported file type. Upload a CSV or Excel file.")
    return None

def _coerce_dataframe(df: pd.DataFrame, mapping: dict, date_format: str | None, invert_amount: bool):
    df2 = df.copy()

    rename_map = {mapping[k]: k for k in mapping}
    df2 = df2.rename(columns=rename_map)

    keep = [c for c in (REQUIRED_FIELDS + OPTIONAL_FIELDS) if c in df2.columns]
    df2 = df2[keep]

    if "date" in df2.columns:
        df2["date"] = pd.to_datetime(df2["date"], format=date_format, errors="coerce").dt.date

    if "amount" in df2.columns:
        df2["amount"] = pd.to_numeric(df2["amount"], errors="coerce")
        if invert_amount:
            df2["amount"] = -df2["amount"]

    if "kind" in df2.columns:
        df2["kind"] = df2["kind"].astype(str).str.strip().str.lower()
        df2["kind"] = df2["kind"].where(df2["kind"].isin(["expense", "income"]), "expense")
    else:
        df2["kind"] = "expense"

    # Defaults
    if "account" in df2.columns:
        df2["account"] = df2["account"].fillna("Cash")
    else:
        df2["account"] = "Cash"

    if "description" not in df2.columns:
        df2["description"] = ""

    df2 = df2.dropna(how="all")

    errors = []
    if df2["date"].isna().any():
        errors.append("Some dates could not be parsed.")
    if df2["amount"].isna().any():
        errors.append("Some amounts are missing or invalid.")
    if "category" not in df2.columns or df2["category"].isna().any():
        errors.append("Some categories are missing.")

    return df2, errors

def render_imports():
    st.subheader("Import transactions")
    st.caption("Upload a CSV or Excel, map columns, preview, and import.")

    upload = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
    if upload is None:
        st.info("Download a template to get started.")
        with st.expander("CSV Template"):
            st.code("date,description,amount,category,account,kind\n2025-09-01,Coffee,3.5,Food,Cash,expense\n", language="csv")
        return

    try:
        raw_df = _parse_file(upload)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return
    if raw_df is None or raw_df.empty:
        st.warning("No rows found in file.")
        return

    st.write("Detected columns:", list(raw_df.columns))

    auto_map = _deduce_mapping(raw_df)
    st.markdown("**Map your columns**")
    cols = st.columns(3)
    with cols[0]:
        date_col = st.selectbox("Date column*", options=["—"] + list(raw_df.columns), index=(["—"]+list(raw_df.columns)).index(auto_map.get("date", "—")) if auto_map.get("date") else 0)
        desc_col = st.selectbox("Description column", options=["—"] + list(raw_df.columns), index=(["—"]+list(raw_df.columns)).index(auto_map.get("description", "—")) if auto_map.get("description") else 0)
    with cols[1]:
        amount_col = st.selectbox("Amount column*", options=["—"] + list(raw_df.columns), index=(["—"]+list(raw_df.columns)).index(auto_map.get("amount", "—")) if auto_map.get("amount") else 0)
        category_col = st.selectbox("Category column*", options=["—"] + list(raw_df.columns), index=(["—"]+list(raw_df.columns)).index(auto_map.get("category", "—")) if auto_map.get("category") else 0)
    with cols[2]:
        account_col = st.selectbox("Account column", options=["—"] + list(raw_df.columns), index=(["—"]+list(raw_df.columns)).index(auto_map.get("account", "—")) if auto_map.get("account") else 0)
        kind_col = st.selectbox("Type column", options=["—"] + list(raw_df.columns), index=(["—"]+list(raw_df.columns)).index(auto_map.get("kind", "—")) if auto_map.get("kind") else 0)

    required_selected = all(c and c != "—" for c in [date_col, amount_col, category_col])
    if not required_selected:
        st.warning("Select at least Date, Amount, and Category columns.")
        return

    mapping = {"date": date_col, "amount": amount_col, "category": category_col}
    if desc_col and desc_col != "—": mapping["description"] = desc_col
    if account_col and account_col != "—": mapping["account"] = account_col
    if kind_col and kind_col != "—": mapping["kind"] = kind_col

    st.markdown("**Parsing options**")
    opt_col1, opt_col2 = st.columns(2)
    with opt_col1:
        date_format = st.text_input("Date format (optional)", placeholder="e.g. %Y-%m-%d")
    with opt_col2:
        invert_amount = st.checkbox("Invert amount sign", value=False)
    create_missing = st.checkbox("Create missing categories", value=True)
    default_kind = st.radio("Default type for new categories", ["expense", "income"], horizontal=True, index=0)

    try:
        norm_df, errors = _coerce_dataframe(raw_df, mapping, date_format or None, invert_amount)
    except Exception as e:
        st.error(f"Error normalizing file: {e}")
        return

    if errors:
        for err in errors:
            st.error(err)

    st.markdown("**Preview (first 20)**")
    st.dataframe(norm_df.head(20), use_container_width=True)

    total_rows = len(norm_df)
    if total_rows == 0:
        st.info("Nothing to import.")
        return

    if st.button(f"Import {total_rows} row(s)"):
        try:
            rows = norm_df.to_dict(orient="records")
            imported = import_rows(rows, create_missing_categories=create_missing, default_kind=default_kind)
            st.success(f"Imported {imported} of {total_rows} row(s).")
            try:
                load_df.clear()
            except Exception:
                st.cache_data.clear()
        except Exception as e:
            st.error(f"Import failed: {e}")
