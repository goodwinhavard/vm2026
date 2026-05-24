import streamlit as st

st.set_page_config(
    page_title="World Cup 2026",
    page_icon="🏆",
    layout="wide",
)

st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.write(
    "World Cup 2026 prediction model. Made by Håvard Goodwin."
)

st.title("Prediction Model for FIFA World Cup 2026")

col1, col2, col3 = st.columns(3)
col1.metric("Host countries", "USA, Canada, Mexico")
col2.metric("Teams", "48")
col3.metric("Start", "June 2026")
