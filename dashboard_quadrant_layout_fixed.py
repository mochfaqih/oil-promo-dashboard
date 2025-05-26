
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

# Load data
data = pd.read_csv("report.csv")
rules = json.load(open("promo_rules_simplified.json"))

# Function to calculate rewards
def calculate_rewards(data, rules):
    merchandise_data = []
    for outlet, group in data.groupby("Nama Toko"):
        outlet_rules = rules.get(outlet, [])
        liters = group["Liter"].sum()

        # iterate rule sets
        for rule in outlet_rules:
            if isinstance(rule, str):
                rule = json.loads(rule)
            reward = rule["reward"]
            threshold = rule["threshold"]
            unit = rule["unit"]

            if unit == "dus":
                qty = group[group["Unit"] == "dus"]["Qty"].sum()
                reward_qty = qty // threshold
            elif unit == "botol":
                qty = group[group["Unit"] == "botol"]["Qty"].sum()
                reward_qty = qty // threshold
            else:
                reward_qty = 0

            if reward_qty > 0:
                merchandise_data.append({
                    "Tanggal": datetime.now().date(),
                    "Outlet": outlet,
                    "Merchandise": reward,
                    "Jumlah": int(reward_qty)
                })

    return pd.DataFrame(merchandise_data)

# Layout and style
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #0052cc, #007fff);
        color: white;
    }
    .block-container {
        padding-top: 1rem;
    }
    .dataframe th {
        background-color: #003366;
        color: white;
        font-weight: bold;
    }
    .dataframe td {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True
)

# Header
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("### Dashboard Monitoring Program Enduro BERSINAR")
with col2:
    st.image("pertamina_lubricants_logo.PNG", width=100)

# Calculate rewards
merch = calculate_rewards(data, rules)

# Layout for 2x2 quadrant style
top_left, top_right = st.columns(2)
bottom_left, bottom_right = st.columns(2)

with top_left:
    st.subheader("Total Produk Terjual per Toko")
    st.dataframe(
        data[["Tanggal", "Nama Toko", "Unit", "Qty", "Liter"]],
        height=200
    )

with top_right:
    st.subheader("Grafik Penjualan")
    summary = data.groupby("Nama Toko")["Liter"].sum()
    fig, ax = plt.subplots(figsize=(4, 4))
    summary.plot(kind="bar", ax=ax, color=["#66ccff", "#cc99ff", "#ff99cc", "#99ff99", "#ffcc99"])
    ax.set_ylabel("Liter Terjual")
    ax.set_xlabel("Toko")
    st.pyplot(fig)

with bottom_left:
    st.subheader("Estimasi Merchandise")
    st.dataframe(merch, height=200)

with bottom_right:
    st.subheader("Ringkasan Data")
    st.dataframe(data.groupby("Nama Toko")[["Qty", "Liter"]].sum(), height=200)
