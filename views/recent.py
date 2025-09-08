import io
import pandas as pd
import streamlit as st
from data.dataframe import load_df

def _prep_display_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["category_id", "id", "created_at"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df.rename(columns={
        "tx_date": "Date",
        "description": "Description",
        "amount": "Amount",
        "category": "Category",
        "account": "Account",
        "category_kind": "Type",
        "created_at": "Created At",
    })

def _make_excel_friendly(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include=["datetimetz"]).columns:
        out[col] = out[col].dt.tz_localize(None)
    for col in out.columns:
        if out[col].dtype == "object":
            conv = pd.to_datetime(out[col], errors="ignore", utc=True)
            if pd.api.types.is_datetime64tz_dtype(conv):
                out[col] = conv.dt.tz_localize(None)
    return out

def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def _df_to_excel_bytes(df: pd.DataFrame, engine: str) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine=engine) as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
    buf.seek(0)
    return buf.getvalue()

def render_recent(start=None, end=None, category_ids=None):
    try:
        df = load_df(start=start, end=end, category_ids=category_ids)
        if df is None or df.empty:
            st.info("No transactions found for the selected filters.")
            return

        display_df = _prep_display_df(df)

        st.download_button(
            "⬇️ Download CSV",
            data=_df_to_csv_bytes(display_df),
            file_name="transactions.csv",
            mime="text/csv",
            key="dl_csv",
        )

        engine = "openpyxl"
        if engine:
            try:
                excel_df = _make_excel_friendly(display_df)
                st.download_button(
                    "⬇️ Download Excel",
                    data=_df_to_excel_bytes(excel_df, engine),
                    file_name="transactions.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_xlsx",
                )
            except Exception as e:
                st.caption(f"Excel export unavailable: {e}")
        else:
            st.caption("Excel export unavailable: install 'openpyxl' or 'XlsxWriter'.")

        st.dataframe(display_df)

    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
