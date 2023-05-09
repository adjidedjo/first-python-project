import mysql.connector
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
# from vega_datasets import data


database = mysql.connector.connect(
    host="192.213.213.200",
    user="root",
    password="Roy@l4b@d!",
    database="sales_mart"
)
cursor = database.cursor()
# col1, col2 = st.columns(3)

def progress_bar():
    import streamlit as st
    import time

    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.1)
        my_bar.progress(percent_complete + 1, text=progress_text)

def main():

    cursor.execute("SELECT brand, total, invoice_date FROM sales_mart.DETAIL_SALES_FOR_FORECASTS")
    result = cursor.fetchall()

    col1, col2, col3 = st.columns(3)

    df = pd.DataFrame(result, columns=['brand', 'total', 'invoice_date'])
    df['total'] = df['total'].astype(float)
    df['invoice_date'] = df['invoice_date'].astype('datetime64[us]')

    year = col3.selectbox("Pilih Tahun", df['invoice_date'].dt.year.unique())
    periode = col2.selectbox("Pilih Periode", ['Month', 'Days', 'Week', 'Quarter'])
    if periode == 'Days':
        periode_value = 'monthdate(invoice_date):O'
        freq = 'D'
    if periode == 'Week':
        periode_value = 'monthdate(invoice_date):O'
        freq = 'W'
    if periode == 'Month':
        periode_value = 'yearmonth(invoice_date):O'
        freq = 'M'
    if periode == 'Quarter':
        periode_value = 'quartermonth(invoice_date):O'
        freq = 'Q'

    df = df.groupby([pd.Grouper(key='invoice_date', freq=freq), 'brand'])['total'].sum().reset_index()

    input_dropdown = alt.binding_select(options=[None] + list(df['brand'].unique()), labels=['All'] + list(df['brand'].unique()), name='Brand')
    selection = alt.selection_single(fields=['brand'], bind=input_dropdown)
    bar_chart = alt.Chart(df[df['invoice_date'].dt.year==year]).mark_line(point=True).encode(
        x=alt.X(periode_value, title='Bulan'),
        y=alt.Y('total', title='Total'),
        color=alt.Color('brand:N', title='brand', scale=alt.Scale(
            range=['#1C3F70', '#776745', '#FAA74B', 'green', '#ACBEDB', 'red'],
            domain=['ELITE', 'LADY', 'ROYAL', 'SERENITY', 'TOTE', 'ACCESSORIES']
        ))
    ).add_selection(
        selection
    ).transform_filter(
        selection
    )

    st.altair_chart(bar_chart, use_container_width=True)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Trend Penjualan</h1>", unsafe_allow_html=True)
    main()