import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados():
    df = pd.read_csv("vendas_farmacia_100k.csv", sep=";")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.year.astype(str) + "-" + df["date"].dt.month.astype(str)
    return df