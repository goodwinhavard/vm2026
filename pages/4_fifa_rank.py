import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="FIFA Rankings", layout="wide")

st.title("FIFA World Rankings")

rank_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fifa_rank.txt')

df = pd.read_csv(rank_path, sep='\t', header=None, names=['Team', 'Points'])
df = df.dropna(subset=['Team'])

st.dataframe(df, use_container_width=True, hide_index=True)
