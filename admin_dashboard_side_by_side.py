
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
import json
import requests
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    body, .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
        font-family: 'Segoe UI', sans-serif;
    }
    .dash-box {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 0 12px rgba(255,255,255,0.05);
        margin-bottom: 2rem;
    }
    table {
        font-size: 14px;
        color: white;
    }
    .dataframe th {
        background-color: #1e40af;
        color: white;
    }
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌌 Dashboard Monitoring Program Enduro BERSINAR")

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

st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("🧪 Total Produk Terjual per Toko")

sales_summary = df.groupby('outlet')['liters_sold'].sum().reset_index().rename(columns={
    'outlet': 'Nama Toko',
    'liters_sold': 'Jumlah Terjual (Liter)'
})

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

# ➡️ Side-by-side table and chart
col1, col2 = st.columns([1.6, 1.2])

with col1:
    st.markdown("### 📋 Tabel Penjualan")
    st.dataframe(sales_summary.style.set_table_styles(
        [{'selector': 'th', 'props': [('background-color', '#1e40af'), ('color', 'white')]}]
    ), use_container_width=True)

with col2:
    st.markdown("### 📊 Grafik")
    colors = ['#60a5fa', '#a78bfa', '#f472b6', '#34d399', '#facc15']
    fig, ax = plt.subplots(figsize=(5, 3), facecolor='#0f172a')
    bars = ax.bar(sales_summary['Nama Toko'], sales_summary['Jumlah Terjual (Liter)'], color=colors[:len(sales_summary)])
    ax.set_facecolor('#0f172a')
    ax.tick_params(axis='x', colors='white', rotation=15)
    ax.tick_params(axis='y', colors='white')
    ax.set_title("Liter Terjual", color='white')
    for i, bar in enumerate(bars):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f"{int(bar.get_height())} L", color='white', ha='center')
    plt.tight_layout()
    st.pyplot(fig)

st.markdown('</div>', unsafe_allow_html=True)

# 🎁 Merchandise box
st.markdown('<div class="dash-box">', unsafe_allow_html=True)
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
st.dataframe(merch_df.style.set_table_styles(
    [{'selector': 'th', 'props': [('background-color', '#1e40af'), ('color', 'white')]}]
), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 📄 Full data log
st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("📄 Report Keseluruhan")
full = df[['date', 'outlet', 'unit', 'quantity', 'liters_sold']].copy()
full.columns = ['Tanggal', 'Nama Toko', 'Unit', 'Qty', 'Liter']
st.dataframe(full.style.set_table_styles(
    [{'selector': 'th', 'props': [('background-color', '#1e40af'), ('color', 'white')]}]
), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
