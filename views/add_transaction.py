import streamlit as st
from services.categories import get_categories, add_category
from services.transactions import add_transaction
from utils.cache import bust_data_cache

def render_add_transaction():
    pending = st.session_state.pop("pending_kind_switch", None)
    if pending is not None:
        st.session_state["tx_kind"] = pending

    col1, col2 = st.columns(2)

    with col1:
        dp = st.date_input("Select a date")
        desc = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")

    with col2:
        selected_kind = st.radio("Type", ["expense", "income"], horizontal=True, key="tx_kind")

        try:
            categories = get_categories(selected_kind)
        except Exception as e:
            st.error(f"Error loading categories: {e}")
            categories = []

        has_categories = bool(categories)

        preselect_name = st.session_state.pop("just_added_cat", None)
        if has_categories:
            index = categories.index(preselect_name) if preselect_name in categories else 0
            category = st.selectbox("Category", categories, index=index, key=f"cat_{selected_kind}")
        else:
            st.info(f"No {selected_kind} categories yet — add one below first.")
            category = None

        account = st.text_input("Account", value="Cash")

    if st.button("Add Transaction", key="add_tx"):
        if amount <= 0:
            st.warning("Amount must be greater than 0.")
        elif not has_categories or not category:
            st.warning(f"No {selected_kind} categories selected. Please add one below first.")
        else:
            try:
                add_transaction(dp, desc, amount, category, account)
                st.success("Transaction added!")
                bust_data_cache()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding transaction: {e}")

    st.markdown("---")
    st.subheader("Add a new category")

    cat_col1, cat_col2 = st.columns([1, 2])
    with cat_col1:
        new_kind = st.radio("Category type", ["expense", "income"], horizontal=True, key="new_kind_radio")
    with cat_col2:
        new_cat = st.text_input("Category name", key="new_cat_name")

    if st.button("Save Category", key="save_cat"):
        name = (new_cat or "").strip()
        if not name:
            st.warning("Please enter a category name.")
        else:
            try:
                add_category(name, new_kind)
                st.session_state["pending_kind_switch"] = new_kind  
                st.session_state["just_added_cat"] = name           
                st.rerun()
            except Exception as e:
                st.error(f"Error adding category: {e}")
