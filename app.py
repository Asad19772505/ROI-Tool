import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

st.set_page_config(layout="wide", page_title="Investment ROI Tracker")

st.title("💹 ROI Investment Tracker")
st.markdown("Upload your investment CSV with **Date, Investment Type, Amount (EUR), Exchange Rate (EUR to USD)**.")

uploaded_file = st.file_uploader("📁 Upload CSV", type=["csv"])

def calculate_roi(df, currency=False):
    df = df.sort_values("Date").copy()
    df["ROI %"] = df["Amount (EUR)"].pct_change() * 100
    if currency:
        df["Amount (USD)"] = df["Amount (EUR)"] * df["Exchange Rate (EUR to USD)"]
        df["ROI % (USD)"] = df["Amount (USD)"].pct_change() * 100
    return df

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values("Date", inplace=True)

    st.success("✅ File uploaded and parsed.")

    # Date filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    start_date, end_date = st.date_input("📆 Filter by Date Range", [min_date, max_date])

    # Filter Data
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    # Split and calculate
    fixed_df = calculate_roi(filtered_df[filtered_df['Investment Type'].str.lower() == 'fixed'])
    variable_df = calculate_roi(filtered_df[filtered_df['Investment Type'].str.lower() == 'variable'])
    currency_df = calculate_roi(filtered_df[filtered_df['Investment Type'].str.lower() == 'currency'], currency=True)

    # Charts
    st.subheader("📈 Fixed Investment ROI %")
    fig1, ax1 = plt.subplots()
    ax1.plot(fixed_df['Date'], fixed_df['ROI %'], marker='o')
    ax1.set_ylabel("ROI %")
    ax1.grid(True)
    st.pyplot(fig1)

    st.subheader("📉 Variable Investment ROI %")
    fig2, ax2 = plt.subplots()
    ax2.plot(variable_df['Date'], variable_df['ROI %'], marker='o', color='orange')
    ax2.set_ylabel("ROI %")
    ax2.grid(True)
    st.pyplot(fig2)

    st.subheader("💱 Currency Investment ROI % (EUR vs USD)")
    fig3, ax3 = plt.subplots()
    ax3.plot(currency_df['Date'], currency_df['ROI %'], label='ROI % (EUR)', marker='o')
    ax3.plot(currency_df['Date'], currency_df['ROI % (USD)'], label='ROI % (USD)', marker='x')
    ax3.set_ylabel("ROI %")
    ax3.legend()
    ax3.grid(True)
    st.pyplot(fig3)

    # Export to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        fixed_df.to_excel(writer, sheet_name='Fixed', index=False)
        variable_df.to_excel(writer, sheet_name='Variable', index=False)
        currency_df.to_excel(writer, sheet_name='Currency', index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download ROI Report (Excel)",
        data=output,
        file_name="ROI_Investment_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
