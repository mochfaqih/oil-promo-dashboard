
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
import json
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

st.title("📊 Admin Monitoring Dashboard")

# Google Sheets config
SHEET_NAME = "OilPromoReports"

# Authenticate using Streamlit secrets
creds = json.loads(st.secrets["GOOGLE_CREDS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(creds, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open(SHEET_NAME)
worksheet = sh.sheet1

promo_rules = {
    'Outlet A': {'T-shirt': 2},
    'Outlet B': {'Cap': 3},
}

merch_stock = {
    'Outlet A': {'T-shirt': 50},
    'Outlet B': {'Cap': 30},
}

try:
    df = get_as_dataframe(worksheet).dropna(how="all")
except:
    st.warning("No reports submitted yet.")
    st.stop()

df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df = df.dropna(subset=['quantity'])

df['liters_sold'] = df.apply(
    lambda row: row['quantity'] * promo_rules[row['outlet']][row['merch_type']],
    axis=1
)

liters_by_outlet = df.groupby('outlet')['liters_sold'].sum().reset_index()

st.subheader("Estimated Oil Sold per Outlet")
st.dataframe(liters_by_outlet)

fig, ax = plt.subplots()
ax.bar(liters_by_outlet['outlet'], liters_by_outlet['liters_sold'])
ax.set_ylabel("Liters Sold")
ax.set_title("Oil Sales Estimation")
st.pyplot(fig)

st.subheader("Remaining Merchandise Stock")
for outlet, merch in merch_stock.items():
    st.markdown(f"**{outlet}**")
    for merch_type, initial_stock in merch.items():
        used = df[(df['outlet'] == outlet) & (df['merch_type'] == merch_type)]['quantity'].sum()
        remaining = initial_stock - used
        st.text(f"{merch_type}: {remaining} remaining (used {used} of {initial_stock})")

st.subheader("📄 All Reports")
st.dataframe(df)
