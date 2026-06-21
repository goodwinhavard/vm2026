import streamlit as st
import pandas as pd
from functions.model_cache import train_and_save_model, get_simulation_results, _real_results_hash

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

st.divider()

num_sims = 100000

with st.spinner("Training model and running simulations..."):
    model, err = train_and_save_model()
    if err:
        st.error(f"Model error: {err}")
        st.stop()
    groups, pos_counts, ko_counts, match_outcomes = get_simulation_results(num_sims, model, _real_results_hash())
    st.session_state["sim_results"] = (groups, pos_counts, ko_counts, match_outcomes)

st.subheader("Top 5 Favorites to Win")
all_teams_list = [team for group in groups.values() for team in group]
win_probabilities = [
    {"Team": team, "Probability of Winning": ko_counts[team].get("Winner", 0) / num_sims}
    for team in all_teams_list
]
top_5_df = pd.DataFrame(win_probabilities).sort_values("Probability of Winning", ascending=False).head(5)
st.table(
    top_5_df.set_index("Team").style.format({"Probability of Winning": "{:.1%}"})
)

st.caption("See the **Prediction Results** page for full group stage, knockout stage, and match probabilities.")
