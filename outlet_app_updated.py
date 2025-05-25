
import streamlit as st
import pandas as pd
import datetime
import gspread
import json
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f9fc;
    }
    .report-box {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="report-box">', unsafe_allow_html=True)
st.title("🧾 Outlet Merchandise Reporting")

# --- Google Sheets config ---
SHEET_NAME = "OilPromoReports"
creds = json.loads(st.secrets["GOOGLE_CREDS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(creds, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open(SHEET_NAME)
worksheet = sh.sheet1

# --- Load promo rules ---
import requests
rules_url = "https://raw.githubusercontent.com/mochfaqih/oil-promo-dashboard/main/promo_rules.json"
promo_rules = json.loads(requests.get(rules_url).text)

outlets = list(promo_rules.keys())
outlet = st.selectbox("Select Your Outlet", outlets)
unit = st.radio("Report by Unit", ["botol", "dus"])
quantity = st.number_input(f"How many {unit} sold?", min_value=1, step=1)
date = st.date_input("Date", datetime.date.today())

if st.button("Submit Report"):
    liters = quantity * 1 if unit == "botol" else quantity * 6
    new_entry = {
        'date': str(date),
        'outlet': outlet,
        'unit': unit,
        'quantity': quantity,
        'liters_sold': liters
    }

    try:
        df = get_as_dataframe(worksheet).dropna(how="all")
    except:
        df = pd.DataFrame(columns=['date', 'outlet', 'unit', 'quantity', 'liters_sold'])

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    set_with_dataframe(worksheet, df)
    st.success("Report submitted successfully!")

st.markdown('</div>', unsafe_allow_html=True)
