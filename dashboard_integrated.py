import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")

# Load credentials
creds_dict = {
  "type": "service_account",
  "project_id": "oilpromoreports",
  "private_key_id": "502f3f780b72e26eeebf760af143356d97889bea",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQChaSaC3saFm+my\n+XJpDkCa9TNZrRb45RiCawNbHs3x8rKoDpreXdDy4m2i+BCgcWKOaW7td00g/hMs\nvFYxzsS53FHoPmF5GDyQHwPoW7TsDNwHj0lUcPFR0nGyrApGjPfiqyYGKjbJrmHd\n1EHzX/fB/mj/SXEVzXLqSLKBMgb1DtOmJNtMUuFGMSaIMGq2Wf02Yot6unj4cMaV\nx0KlmGvIPwbdjfBVvRw8+/evpoC+HUO3PqCPwZ0eHrCQckAc1GBOVS2u36Y6J/DF\nCDa8bHXoQJmaMmPHVGcC3C1deNRgjZ1g7ryXSRzwkzXsjyjnRYr+M1yqACyK8eOZ\nq7TvBrTnAgMBAAECggEAFlLcqKz29/OgVsh5Ml5uQQA4oeZ2juXghekXBbs08ImI\nfAXJFYgUJgN69lcotYf5AYlDdkRRvoZlUIKbyTe3rZzzFxPJl13qwmQHvlMwqpT8\nuW7vzWXxekeIwhVZNni4r/jLwX6FJU+g6XU5ydc0BPiSvPwDT+iiRBTZ21R38dxq\n...
  "client_email": "oilpromo-sheet-bot@oilpromoreports.iam.gserviceaccount.com",
  "client_id": "102547412670813222092",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/oilpromo-sheet-bot%40oilpromoreports.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

creds = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(creds)

# Access the sheet
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1E30QkUBWbhnz3-AGc28BHPB2zG9gyVbankSm8bsbphk/edit#gid=0")
worksheet = spreadsheet.sheet1
records = worksheet.get_all_records()
df = pd.DataFrame(records)

# Display
st.title("📊 Dashboard Monitoring Program Enduro BERSINAR")
st.dataframe(df, use_container_width=True)