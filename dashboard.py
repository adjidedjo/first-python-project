import mysql.connector
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
# import plotly.graph_objects as go
# from vega_datasets import data


database = mysql.connector.connect(
    host="192.213.213.200",
    user="root",
    password="Roy@l4b@d!",
    database="sales_mart"
)
cursor = database.cursor()

def groupedbarchart(df, freq, year):
    df = df.groupby([pd.Grouper(key='invoice_date', freq='Y'), 'brand', 'customer_type'])['total'].sum().reset_index()
    df = df[df['invoice_date'].dt.year==year]
    df = df.drop(columns=['invoice_date'], axis=1).reset_index()
    df = df.query("customer_type in ('DIRECT', 'RETAIL', 'MODERN MARKET')")
    # df = df.reset_index(inplace=True)
    # df = df.rename(columns={'index': 'group'}, inplace=True)
    barchart = px.bar(
        df,
        x = "brand",
        y = "total",
        color= 'customer_type',
        labels={"brand": "Brand",
                "total": "Total Sales",
                "customer_type": "Channel"},
        barmode = 'group',
        title='Channel per Tahun',
    )
    barchart.update_layout(width=800)
    barchart.update_traces(textposition='inside')
    st.write(barchart)
    # print(df)


def linechart(df, periode_value, freq, year):

    df = df.groupby([pd.Grouper(key='invoice_date', freq=freq), 'brand'])['total'].sum().reset_index()

    input_dropdown = alt.binding_select(options=[None] + list(df['brand'].unique()), labels=['All'] + list(df['brand'].unique()), name='Brand')
    selection = alt.selection_single(fields=['brand'], bind=input_dropdown)

    line_chart = alt.Chart(df[df['invoice_date'].dt.year==year]).mark_line(point=True).encode(
        x=alt.X(periode_value, title='Periode'),
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

    st.altair_chart(line_chart, use_container_width=True)

def piechart(df, freq, year):
    df = df.groupby([pd.Grouper(key='invoice_date', freq=freq), 'brand'])['total'].sum().reset_index()
    df = df[df['invoice_date'].dt.year==year]
    pie_chart = px.pie(df, values='total', names='brand',
                       color_discrete_map={'ELITE': 'lightcyan',
                                           'SERENITY': '#00CC96',
                                           'LADY': '#FF6692',
                                           'ROYAL': '#FF97FF',
                                           'TOTE': '#FECB52',
                                           'ACCESSORIES': '#EF553B',
                                           })
    pie_chart.update_layout(width=500)
    pie_chart.update_traces(textposition='inside', textinfo='percent+label')
    st.write(pie_chart)

def main():

    cursor.execute("SELECT brand, total, invoice_date, customer_type FROM sales_mart.DETAIL_SALES_FOR_FORECASTS")
    result = cursor.fetchall()

    col1, col2 = st.columns([2,3])

    df = pd.DataFrame(result, columns=['brand', 'total', 'invoice_date', 'customer_type'])
    df['total'] = df['total'].astype(float)
    df['invoice_date'] = df['invoice_date'].astype('datetime64[us]')

    year = st.sidebar.selectbox("Pilih Tahun", df['invoice_date'].dt.year.unique())
    periode = st.sidebar.selectbox("Pilih Periode", ['Month', 'Days', 'Week', 'Quarter'])
    # sidebar(df)
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

    #show the chart using merge column format    
    with col1:
        piechart(df, freq, year)
        groupedbarchart(df, freq, year)
    with col2:
        linechart(df, periode_value, freq, year)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Trend Penjualan</h1>", unsafe_allow_html=True)
    main()