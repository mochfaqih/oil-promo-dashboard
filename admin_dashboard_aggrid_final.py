
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

st.markdown("""
    <style>
    body, .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    .ag-header-cell-label {
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
    }
    .ag-cell {
        color: white !important;
        font-size: 15px;
        font-weight: bold;
        text-align: center !important;
    }
    .ag-theme-streamlit {
        --ag-background-color: #0f172a;
        --ag-header-background-color: #3b82f6;
        --ag-foreground-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title with logo
st.markdown(
    """
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h1 style='font-size: 40px; margin-bottom: 20px;'>🌌 Dashboard Monitoring Program Enduro BERSINAR</h1>
        <img src="https://raw.githubusercontent.com/mochfaqih/oil-promo-dashboard/main/pertamina_lubricants_logo.png" alt="logo" width="220">
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

try:
    df = get_as_dataframe(worksheet).dropna(how="all")
except:
    st.warning("Belum ada laporan dari outlet.")
    st.stop()

df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df = df.dropna(subset=['quantity'])

if 'liters_sold' not in df.columns:
    df['liters_sold'] = df.apply(lambda row: row['quantity'] * (6 if row['unit'] == 'dus' else 1), axis=1)
else:
    df['liters_sold'] = pd.to_numeric(df['liters_sold'], errors='coerce')

# Summary Table
st.subheader("🧪 Total Produk Terjual per Toko")
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

col1, col2 = st.columns([1.6, 1.2])
with col1:
    st.markdown("### 📋 Tabel Penjualan")
    gb = GridOptionsBuilder.from_dataframe(sales_summary)
    gb.configure_default_column(
        cellStyle={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '15px'},
        headerClass="custom-header"
    )
    grid_options = gb.build()
    AgGrid(sales_summary, gridOptions=grid_options, theme='streamlit', fit_columns_on_grid_load=True)

with col2:
    st.markdown("### 📊 Grafik")
    colors = ['#60a5fa', '#a78bfa', '#f472b6', '#34d399', '#facc15']
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='#0f172a')
    bars = ax.bar(sales_summary['Nama Toko'], sales_summary['Jumlah Terjual (Liter)'], color=colors[:len(sales_summary)])
    ax.set_facecolor('#0f172a')
    ax.tick_params(axis='x', colors='white', rotation=15)
    ax.tick_params(axis='y', colors='white')
    ax.set_title("Liter Terjual", color='white')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f"{int(bar.get_height())} L", color='white', ha='center')
    plt.tight_layout()
    st.pyplot(fig)

# Merchandise
st.subheader("🎁 Sisa Merchandise")
merch_summary = []
for outlet in df['outlet'].unique():
    outlet_df = df[df['outlet'] == outlet]
    botol = outlet_df[outlet_df['unit'] == 'botol']['quantity'].sum()
    dus = outlet_df[outlet_df['unit'] == 'dus']['quantity'].sum()
    date_used = outlet_df['date'].max()
    for merch, rule in promo_rules.get(outlet, {}).items():
        qty = int(botol // rule['qty']) if rule['unit'] == 'botol' else int(dus // rule['qty'])
        if qty > 0:
            merch_summary.append({
                "Tanggal": date_used,
                "Nama Toko": outlet,
                "Item": merch,
                "Terpakai": qty
            })
merch_df = pd.DataFrame(merch_summary)
merch_df['Pengadaan'] = 50
merch_df['Sisa'] = merch_df['Pengadaan'] - merch_df['Terpakai']
merch_df = merch_df[['Nama Toko', 'Item', 'Pengadaan', 'Terpakai', 'Sisa', 'Tanggal']]
gb_merch = GridOptionsBuilder.from_dataframe(merch_df)
gb_merch.configure_default_column(
    cellStyle={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '15px'},
    headerClass="custom-header"
)
AgGrid(merch_df, gridOptions=gb_merch.build(), theme='streamlit', fit_columns_on_grid_load=True)

# Raw Report
st.subheader("📄 Report Keseluruhan")
full = df[['date', 'outlet', 'unit', 'quantity', 'liters_sold']].copy()
full.columns = ['Tanggal', 'Nama Toko', 'Unit', 'Qty', 'Liter']
full['Qty'] = full['Qty'].astype(int)
full['Liter'] = full['Liter'].astype(int)
gb_full = GridOptionsBuilder.from_dataframe(full)
gb_full.configure_default_column(
    cellStyle={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '15px'},
    headerClass="custom-header"
)
AgGrid(full, gridOptions=gb_full.build(), theme='streamlit', fit_columns_on_grid_load=True)
