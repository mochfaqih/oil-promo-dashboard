
import streamlit as st
import pandas as pd
import datetime
import gspread
import json
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

st.title("📋 Outlet Merchandise Reporting")

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

outlet = st.selectbox("Select Outlet", list(promo_rules.keys()))
merch_type = st.selectbox("Merchandise Type", list(promo_rules[outlet].keys()))
quantity = st.number_input("How many items given out?", min_value=1, step=1)
date = st.date_input("Date", datetime.date.today())

if st.button("Submit Report"):
    new_entry = {
        'date': str(date),
        'outlet': outlet,
        'promo': f"Buy {promo_rules[outlet][merch_type]}L get 1 {merch_type}",
        'merch_type': merch_type,
        'quantity': quantity
    }

    try:
        df = get_as_dataframe(worksheet).dropna(how="all")
    except:
        df = pd.DataFrame(columns=['date', 'outlet', 'promo', 'merch_type', 'quantity'])

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    set_with_dataframe(worksheet, df)
    st.success("Report submitted successfully!")
