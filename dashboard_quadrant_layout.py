import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
import json
import requests
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# Blue gradient background + refined table styles
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(to bottom, #0d47a1, #1976d2);
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.block-container {
    padding-top: 2rem;
}
.ag-theme-streamlit .ag-header-cell-label {
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 16px;
}
.ag-theme-streamlit .ag-cell {
    color: white;
    font-size: 15px;
    font-weight: bold;
    text-align: center;
}
.ag-theme-streamlit {
    --ag-background-color: transparent;
    --ag-header-background-color: #1e3a8a;
    --ag-foreground-color: white;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h1 style='font-size: 40px; margin-bottom: 20px;'>📊 Dashboard Monitoring Program Enduro BERSINAR</h1>
        <img src="pertamina_lubricants_logo.PNG" alt="logo" width="200">
    </div>
    """, unsafe_allow_html=True
)

rules_url = "https://raw.githubusercontent.com/mochfaqih/oil-promo-dashboard/main/promo_rules_simplified.json"
promo_rules = json.loads(requests.get(rules_url).text)

SHEET_NAME = "OilPromoReports"
creds = json.loads(st.secrets["GOOGLE_CREDS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(creds, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open(SHEET_NAME)
worksheet = sh.sheet1

df = get_as_dataframe(worksheet).dropna(how="all")
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df = df.dropna(subset=['quantity'])
if 'liters_sold' not in df.columns:
    df['liters_sold'] = df.apply(lambda row: row['quantity'] * (6 if row['unit'] == 'dus' else 1), axis=1)
else:
    df['liters_sold'] = pd.to_numeric(df['liters_sold'], errors='coerce')

# Sales summary
sales_summary = df.groupby('outlet')['liters_sold'].sum().reset_index().rename(columns={
    'outlet': 'Nama Toko',
    'liters_sold': 'Jumlah Terjual (Liter)'
})
sales_summary['Jumlah Terjual (Liter)'] = sales_summary['Jumlah Terjual (Liter)'].astype(int)
history_so = {
    "Gedang Motor": 660,
    "Restu Motor": 1240,
    "Mandiri Motor": 278,
    "Jitu Motor": 267,
    "Hasil Abadi 3 Motor": 84
}
growth_dummy = {
    "Gedang Motor": "12%",
    "Restu Motor": "11%",
    "Mandiri Motor": "10%",
    "Jitu Motor": "12%",
    "Hasil Abadi 3 Motor": "5%"
}
sales_summary['History avg. SO/bulan (Q1’25)'] = sales_summary['Nama Toko'].map(history_so)
sales_summary['Growth'] = sales_summary['Nama Toko'].map(growth_dummy)
sales_summary = sales_summary[['Nama Toko', 'History avg. SO/bulan (Q1’25)', 'Jumlah Terjual (Liter)', 'Growth']]

# Top row: Table (left), Plot (right)
col1, col2 = st.columns([1.5, 1])
with col1:
    st.markdown("### 📋 Total Produk Terjual per Toko")
    gb = GridOptionsBuilder.from_dataframe(sales_summary)
    gb.configure_default_column(cellStyle={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '15px'})
    AgGrid(sales_summary, gridOptions=gb.build(), theme='streamlit', fit_columns_on_grid_load=True)

with col2:
    st.markdown("### 📊 Grafik Penjualan")
    fig, ax = plt.subplots(figsize=(4.5, 3), facecolor='none')
    colors = ['#60a5fa', '#a78bfa', '#f472b6', '#34d399', '#facc15']
    bars = ax.bar(sales_summary['Nama Toko'], sales_summary['Jumlah Terjual (Liter)'], color=colors)
    ax.set_facecolor('none')
    ax.tick_params(axis='x', colors='white', rotation=15)
    ax.tick_params(axis='y', colors='white')
    ax.set_title("Liter Terjual", color='white')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f"{int(bar.get_height())} L", color='white', ha='center')
    plt.tight_layout()
    st.pyplot(fig)

# Bottom row: 2 tables
col3, col4 = st.columns(2)
with col3:
    st.markdown("### 📄 Report Keseluruhan")
    full_table = df[['date', 'outlet', 'unit', 'quantity', 'liters_sold']].copy()
    full_table.columns = ['Tanggal', 'Nama Toko', 'Unit', 'Qty', 'Liter']
    full_table['Liter'] = full_table['Liter'].astype(int)
    AgGrid(full_table, theme='streamlit', fit_columns_on_grid_load=True)

with col4:
    st.markdown("### 🎁 Estimasi Merchandise")
    rewards = []
    for outlet, rules in promo_rules.items():
        df_outlet = df[df['outlet'] == outlet]
        total_dus = df_outlet[df_outlet['unit'] == 'dus']['quantity'].sum()
        total_bottle = df_outlet[df_outlet['unit'] == 'botol']['quantity'].sum()
        reward_dict = {}
        for rule in rules:
            reward = rule['reward']
            qty = 0
            if rule['unit'] == 'dus':
                qty = int(total_dus // rule['required_qty'])
            else:
                qty = int(total_bottle // rule['required_qty'])
            if reward not in reward_dict:
                reward_dict[reward] = 0
            reward_dict[reward] += qty
        for reward, qty in reward_dict.items():
            if qty > 0:
                rewards.append({'Nama Toko': outlet, 'Merchandise': reward, 'Qty': qty})
    reward_df = pd.DataFrame(rewards)
    AgGrid(reward_df, theme='streamlit', fit_columns_on_grid_load=True)