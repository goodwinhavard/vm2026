import streamlit as st

st.set_page_config(
    page_title="World Cup 2026",
    page_icon="🏆",
    layout="wide",
)

st.sidebar.title("Navigation")
st.sidebar.info("Use the Streamlit page menu to open the Tipping subpage.")
st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.write(
    "World Cup 2026 tipping competition where you can preview groups, follow tournament updates, "
    "and make predictions."
)

st.title("World Cup 2026")
st.header("Prediksjonsmodell for FIFA World Cup 2026")

col1, col2, col3 = st.columns(3)
col1.metric("Host countries", "USA, Canada, Mexico")
col2.metric("Teams", "48")
col3.metric("Start", "June 2026")

st.markdown("### Groups preview")
st.write(
    "Group details and match schedules will be added as the tournament draws nearer. "
    "Stay tuned for team lists, fixtures, and knockout path updates."
)
