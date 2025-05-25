
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
    .stApp { background-color: #f4f6f8; }
    .dash-box {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Admin Dashboard – Promo Monitoring")

# Load promo rules
rules_url = "https://raw.githubusercontent.com/mochfaqih/oil-promo-dashboard/main/promo_rules.json"
promo_rules = json.loads(requests.get(rules_url).text)

# Load sheet
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
    st.warning("No reports yet.")
    st.stop()

df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['liters_sold'] = pd.to_numeric(df['liters_sold'], errors='coerce')
df = df.dropna(subset=['quantity', 'liters_sold'])

# Aggregate by outlet
summary = df.groupby('outlet')['liters_sold'].sum().reset_index()

st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("🔢 Total Estimated Liters Sold per Outlet")
st.dataframe(summary)

fig, ax = plt.subplots()
ax.bar(summary['outlet'], summary['liters_sold'], color="#0066cc")
ax.set_ylabel("Liters Sold")
ax.set_title("Oil Sales Estimation")
st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

# Calculate rewards
st.markdown('<div class="dash-box">', unsafe_allow_html=True)
st.subheader("🎁 Estimated Merchandise to Be Given")

merch_report = []
for outlet in df['outlet'].unique():
    outlet_df = df[df['outlet'] == outlet]
    total_botol = (
        outlet_df[outlet_df['unit'] == 'botol']['quantity'].sum() +
        outlet_df[outlet_df['unit'] == 'dus']['quantity'].sum() * 6
    )
    for merch, rule in promo_rules[outlet].items():
        unit = rule['unit']
        per = rule['qty']
        total_units = outlet_df[outlet_df['unit'] == unit]['quantity'].sum()
        units_as_botol = total_units * 6 if unit == 'dus' else total_units
        rewards = int(units_as_botol // (per if unit == 'botol' else per * 6))
        merch_report.append({
            'Outlet': outlet,
            'Merchandise': merch,
            'Reward Qty': rewards
        })

merch_df = pd.DataFrame(merch_report)
st.dataframe(merch_df)
st.markdown('</div>', unsafe_allow_html=True)
