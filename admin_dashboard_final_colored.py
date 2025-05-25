
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import gspread
import json
import requests
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    body, .stApp {
        background-color: #f1f6fb;
        color: #1f2e4d;
        font-family: 'Segoe UI', sans-serif;
    }
    .dash-box {
        background: linear-gradient(135deg, #e0f1ff, #ffffff);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    table {
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Monitoring Program “Enduro BERSINAR”")

# Load rules
rules_url = "https://raw.githubusercontent.com/mochfaqih/oil-promo-dashboard/main/promo_rules_simplified.json"
promo_rules = json.loads(requests.get(rules_url).text)

# Load spreadsheet
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

# Liter otomatis
if 'liters_sold' not in df.columns:
    df['liters_sold'] = df.apply(lambda row: row['quantity'] * (6 if row['unit'] == 'dus' else 1), axis=1)
else:
    df['liters_sold'] = pd.to_numeric(df['liters_sold'], errors='coerce')

# 💧 Penjualan Total per Toko
st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("🛢️ Total Produk Terjual per Toko")

sales_summary = df.groupby('outlet')['liters_sold'].sum().reset_index().rename(columns={
    'outlet': 'Nama Toko',
    'liters_sold': 'Jumlah Terjual (Liter)'
})

# Map dummy SO and Growth
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

# Reorder columns
sales_summary = sales_summary[['Nama Toko', 'History avg. SO/bulan (Q1’25)', 'Jumlah Terjual (Liter)', 'Growth']]
st.dataframe(sales_summary, use_container_width=True)

# ✨ Grafik Baru: Horizontal bar with Pertamina color theme
st.markdown("### 📉 Grafik Penjualan")
fig, ax = plt.subplots(figsize=(6, 3))  # smaller and wide

colors = ['#007bff', '#1d4ed8', '#2563eb', '#0ea5e9', '#ef4444']
ax.barh(sales_summary['Nama Toko'], sales_summary['Jumlah Terjual (Liter)'], color=colors[:len(sales_summary)])

ax.set_xlabel("Liter")
ax.set_title("Liter Oli Terjual per Outlet", fontsize=12)
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
plt.tight_layout()
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)
