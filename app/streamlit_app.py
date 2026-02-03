import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config for wide layout
st.set_page_config(layout="wide")

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

DATA = ROOT / "data"

df_cb_unified = pd.read_csv(DATA / "df_cb_unified.csv")
df_match = pd.read_csv(DATA / "df_matched.csv")
df_cb_remaining = pd.read_csv(DATA / "df_cb_remaining.csv")
df_bs_remaining = pd.read_csv(DATA / "df_bs_remaining.csv")

st.title("Bank Reconciliation Results")

st.sidebar.header("Settings")
selected_date = st.sidebar.date_input("Select Date", value=pd.Timestamp.now())


def create_gauge_chart(value, chart_name, min_val=0, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%"},
        title={"text": chart_name},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "threshold": {"line": {"color": "red", "width": 4}, "value": 90},
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

# --- Filter data ---
def filter_by_date(df, date_col, start_date, end_date):
    if date_col not in df.columns:
        return df  # fallback if no date col
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df[
        (df[date_col].dt.date >= start_date) &
        (df[date_col].dt.date <= end_date)
    ].copy()

df_match_filt = filter_by_date(df_match, "DATE", selected_date, selected_date)
df_unmatched_cb_filt = filter_by_date(df_cb_remaining, "DATE", selected_date, selected_date)
df_unmatched_bs_filt = filter_by_date(df_bs_remaining, "DATE", selected_date, selected_date)

# --- Calculate totals (filtered) ---
total_transactions_cb = len(df_cb_unified)
total_matched = len(df_match_filt)

matched_pct = (total_matched / total_transactions_cb * 100) if total_transactions_cb else 0

# --- Gauge ---
st.subheader("Matched % of Transactions")
create_gauge_chart(matched_pct, "Matched Transactions", min_val=0, max_val=100)

# --- Bottom metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total transactions (cashbook)", total_transactions_cb)
col2.metric("Total matched", total_matched)
col3.metric("Matched %", f"{matched_pct:.1f}%")

# Optional: show filtered tables for debugging
with st.expander("Show filtered data"):
    st.write("Filtered cashbook")
    st.dataframe(df_cb_unified, use_container_width=True)
    st.write("Filtered matched")
    st.dataframe(df_match_filt, use_container_width=True)

st.subheader("Reconciliation Tables")
st.markdown("""
##### Matched Transactions
This table contains transactions that were successfully matched between the cashbook and the bank statement
based on amount, date, and reference. No further action required on these items.

##### Unmatched Cashbook Transactions
This table shows cashbook transactions that are not yet appeared on the bank statement.
Typically **outstanding deposits** or **unpresented payments** and are expected to clear in a future period.

##### Unmatched Bank Statement Transactions
This table includes bank statement items that do not appear in the cashbook.
These usually require **journal entries** (e.g. bank charges, direct debits, or interest).
""")

tab1, tab2, tab3 = st.tabs(["Matched", "Unmatched Cashbook", "Unmatched Bank Statement"])

with tab1:
    st.write(f"Rows: {len(df_match_filt)}")
    st.dataframe(df_match_filt, use_container_width=True)

with tab2:
    st.write(f"Rows: {len(df_cb_remaining)}")
    st.dataframe(df_cb_remaining, use_container_width=True)

with tab3:
    st.write(f"Rows: {len(df_bs_remaining)}")
    st.dataframe(df_bs_remaining, use_container_width=True)

st.download_button(
    "Download matched CSV",
    df_match_filt.to_csv(index=False).encode("utf-8"),
    file_name="matched_filtered.csv",
    mime="text/csv"
)

search = st.text_input("Search details")
if search:
    df_match_filt = df_match_filt[df_match_filt.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
