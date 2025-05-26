
import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
import json
from oauth2client.service_account import ServiceAccountCredentials

# ----- CONFIGURATION -----
st.set_page_config(page_title="Dashboard Monitoring Program Enduro BERSINAR", layout="wide")

st.markdown(
    """
    <style>
        body {
            background: linear-gradient(to bottom right, #0f4c75, #3282b8);
        }
        .stApp {
            font-family: 'Segoe UI', sans-serif;
        }
        .css-1d391kg {  /* Table header style */
            background-color: #1b262c;
            color: white;
            font-weight: bold;
        }
        th, td {
            text-align: center !important;
        }
        .dataframe th {
            font-weight: bold;
            background-color: #3282b8;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True
)

# ----- HEADER -----
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown("## 📊 Dashboard Monitoring Program Enduro BERSINAR")
with col2:
    st.image("pertamina_lubricants_logo.PNG", width=120)

# ----- LOAD GOOGLE SHEET -----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_CREDS"], scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(st.secrets["SHEET_URL"])
worksheet = sheet.get_worksheet(0)
df = get_as_dataframe(worksheet, evaluate_formulas=True).dropna(how="all")

# ----- DISPLAY IN QUADRANT STYLE -----
upper_left, upper_right = st.columns(2)
lower_left, lower_right = st.columns(2)

with upper_left:
    st.markdown("### 🏪 Total Produk Terjual per Toko")
    sales_summary = df[["Tanggal", "Nama Toko", "Unit", "Qty", "Liter"]]
    st.dataframe(sales_summary, use_container_width=True, hide_index=True)

with upper_right:
    st.markdown("### 📈 Grafik Penjualan (Liter)")
    df_summary = df.groupby("Nama Toko").agg({"Liter": "sum"}).reset_index()
    fig = df_summary.plot(kind="bar", x="Nama Toko", y="Liter", color="#bbe1fa", legend=False).get_figure()
    st.pyplot(fig, clear_figure=True)

with lower_left:
    st.markdown("### 🎁 Estimasi Merchandise")
    merch = df[["Nama Toko", "Unit", "Qty"]].copy()
    st.dataframe(merch, use_container_width=True, hide_index=True)

with lower_right:
    st.markdown("### 📄 Ringkasan Transaksi")
    st.dataframe(df[["Tanggal", "Nama Toko", "Promo", "Qty", "Liter"]], use_container_width=True, hide_index=True)
