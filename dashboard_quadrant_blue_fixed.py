
import streamlit as st
import pandas as pd
import json
import gspread
from gspread_dataframe import get_as_dataframe
from datetime import date

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(to bottom, #0052cc, #0073e6);
            color: white;
        }
        .block-container {
            padding-top: 2rem;
        }
        th {
            font-weight: bold !important;
            text-align: center !important;
            background-color: #014f86 !important;
            color: white !important;
        }
        td {
            text-align: center !important;
        }
        .dataframe-container {
            overflow-x: auto;
        }
    </style>
    """, unsafe_allow_html=True
)

# --- Header ---
cols = st.columns([10, 2])
with cols[0]:
    st.markdown("## 📊 Dashboard Monitoring Program Enduro BERSINAR")
with cols[1]:
    st.image("pertamina_lubricants_logo.PNG", width=140)

# --- Google Sheets Access ---
creds = json.loads(st.secrets["GOOGLE_CREDS"])
gc = gspread.service_account_from_dict(creds)
sheet = gc.open_by_url(st.secrets["SHEET_URL"])
ws = sheet.worksheet("Sheet1")
df = get_as_dataframe(ws)
df = df.dropna(how="all")  # remove empty rows

# --- Data Preparation ---
df["liters_sold"] = pd.to_numeric(df["liters_sold"], errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["Tanggal"] = pd.to_datetime(df["date"]).dt.date
sales_summary = df.groupby("outlet")["liters_sold"].sum().reset_index()

# --- Layout ---
top_left, top_right = st.columns(2)
bottom_left, bottom_right = st.columns(2)

with top_left:
    st.markdown("### 🛍️ Total Produk Terjual per Toko")
    sales_df = pd.DataFrame({
        "Nama Toko": sales_summary["outlet"],
        "Total Terjual (Liter)": sales_summary["liters_sold"].astype(int)
    })
    st.dataframe(sales_df, use_container_width=True, height=300)

with top_right:
    st.markdown("### 📈 Grafik Penjualan")
    chart = sales_summary.set_index("outlet")
    st.bar_chart(chart, use_container_width=True)

with bottom_left:
    st.markdown("### 📋 Report Keseluruhan")
    display_cols = ["Tanggal", "outlet", "unit", "quantity", "liters_sold"]
    rename_cols = ["Tanggal", "Nama Toko", "Unit", "Qty", "Liter"]
    full_df = df[display_cols].copy()
    full_df.columns = rename_cols
    full_df["Liter"] = full_df["Liter"].astype(int)
    st.dataframe(full_df, use_container_width=True, height=300)

with bottom_right:
    st.markdown("### 🎁 Estimasi Merchandise")
    # Dummy logic: 1 kaos per 3 dus, 1 kanebo per 2 botol
    reward_summary = []
    for outlet in df["outlet"].unique():
        outlet_df = df[df["outlet"] == outlet]
        total_dus = outlet_df[outlet_df["unit"] == "dus"]["quantity"].sum()
        total_botol = outlet_df[outlet_df["unit"] == "botol"]["quantity"].sum()
        reward_summary.append({
            "Nama Toko": outlet,
            "Kaos": int(total_dus // 3),
            "Kanebo": int(total_botol // 2)
        })
    reward_df = pd.DataFrame(reward_summary)
    st.dataframe(reward_df, use_container_width=True, height=300)
