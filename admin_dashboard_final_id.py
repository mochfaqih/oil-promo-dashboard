
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

# Tambahkan kolom history SO dan growth dummy
sales_summary['History avg. SO/bulan (Q1’25)'] = [660, 1240, 278, 267, 84]
sales_summary['Growth'] = ["12%", "11%", "10%", "12%", "5%"]

# Reorder columns
sales_summary = sales_summary[['Nama Toko', 'History avg. SO/bulan (Q1’25)', 'Jumlah Terjual (Liter)', 'Growth']]
st.dataframe(sales_summary, use_container_width=True)

# Grafik
fig, ax = plt.subplots()
ax.bar(sales_summary['Nama Toko'], sales_summary['Jumlah Terjual (Liter)'], color="#3282b8")
ax.set_title("Total Produk Terjual per Toko")
ax.set_ylabel("Liter")
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

# 🎁 Estimasi Merchandise
st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("🎁 Sisa Merchandise")

merch_summary = []

for outlet in df['outlet'].unique():
    outlet_df = df[df['outlet'] == outlet]
    botol = outlet_df[outlet_df['unit'] == 'botol']['quantity'].sum()
    dus = outlet_df[outlet_df['unit'] == 'dus']['quantity'].sum()
    date_used = outlet_df['date'].max()

    for merch, rule in promo_rules.get(outlet, {}).items():
        if rule['unit'] == 'botol':
            jumlah = int(botol // rule['qty'])
        else:
            jumlah = int(dus // rule['qty'])

        if jumlah > 0:
            merch_summary.append({
                "Tanggal": date_used,
                "Nama Toko": outlet,
                "Item": merch,
                "Terpakai": jumlah
            })

merch_df = pd.DataFrame(merch_summary)
merch_df['Pengadaan'] = 50
merch_df['Sisa'] = merch_df['Pengadaan'] - merch_df['Terpakai']
merch_df = merch_df[['Nama Toko', 'Item', 'Pengadaan', 'Terpakai', 'Sisa', 'Tanggal']]
st.dataframe(merch_df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 📄 Tabel Laporan Mentah
st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("📄 Report Keseluruhan")
full = df.copy()
full = full[['date', 'outlet', 'unit', 'quantity', 'liters_sold']]
full.columns = ['Tanggal', 'Nama Toko', 'Unit', 'Qty', 'Liter']
st.dataframe(full)
st.markdown('</div>', unsafe_allow_html=True)
