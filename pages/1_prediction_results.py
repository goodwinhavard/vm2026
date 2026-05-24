import streamlit as st
import pandas as pd
import os
from train_poisson_model import train_poisson_model
from simulate_world_cup import run_full_simulation

st.set_page_config(page_title="World Cup 2026 Simulation", layout="wide")


@st.cache_resource
def train_and_save_model():
    """Train the Poisson model and save it to pickle file."""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'training_data_fra_kvalikk_og_hist.csv')
    if not os.path.exists(csv_path):
        return None, f"Training CSV not found: {csv_path}"
    
    df = pd.read_csv(csv_path)
    
    # Read custom matches if available
    custom_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'custom_matches_manuell.csv')
    if os.path.exists(custom_path):
        custom_df = pd.read_csv(custom_path)
        
        # Align custom generated match columns with the training data schema
        custom_df = custom_df.rename(
            columns={
                'team1': 'home_team',
                'team2': 'away_team',
                'team1_goals': 'home_goal',
                'team2_goals': 'away_goal',
                'Home-Team': 'home_team',
                'Away-Team': 'away_team',
                'Home-Goals': 'home_goal',
                'Away-Goals': 'away_goal',
            }
        )
        
        expected_cols = ['home_team', 'away_team', 'home_goal', 'away_goal']
        if not set(expected_cols).issubset(custom_df.columns):
            missing = sorted(set(expected_cols) - set(custom_df.columns))
            return None, f"custom_matches.csv is missing required columns: {missing}"
        
        custom_df = custom_df[expected_cols]
        df = pd.concat([df, custom_df], ignore_index=True, sort=False)
    
    # Rename columns to match the trainer's expectations
    mapping = {
        'home_team': 'Home Team',
        'away_team': 'Away Team',
        'home_goal': 'Home Score',
        'away_goal': 'Away Score',
    }
    df = df.rename(columns=mapping)
    
    model, err = train_poisson_model(df)
    if err:
        return None, f"Training failed: {err}"
    
    return model, None

st.title("🏆 World Cup 2026 Predictions")
st.markdown("""
This page shows the probabilities of each team reaching various stages of the 2026 World Cup, 
calculated using a Poisson-based prediction model trained on historical and qualifying data.
""")

# Train model first
with st.spinner("Training Poisson model..."):
    model, err = train_and_save_model()
    if err:
        st.error(f"Model training failed: {err}")
        st.stop()
    
st.success(f"✓ Model trained on {len(model['teams'])} teams")

num_sims = 10000


with st.spinner(f"Running {num_sims} tournament simulations..."):
    groups, pos_counts, ko_counts = run_full_simulation(num_sims, model=model)
    
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

st.header("1. Group Stage Probabilities")
st.write("Chance of finishing in each position within the group.")

# Create columns for group display (3 per row)
cols = st.columns(3)
sorted_group_names = sorted(groups.keys())

for i, group_name in enumerate(sorted_group_names):
    col_idx = i % 3
    with cols[col_idx]:
        st.subheader(group_name)
        teams_in_group = groups[group_name]
        # Sort teams by their probability of finishing at the top of the group
        sorted_teams = sorted(teams_in_group, key=lambda t: pos_counts[group_name][t], reverse=True)
        
        group_data = []
        for team in sorted_teams:
            counts = pos_counts[group_name][team]
            group_data.append({
                "Team": team,
                "1st": f"{counts[0]/num_sims:.0%}",
                "2nd": f"{counts[1]/num_sims:.0%}",
                "3rd": f"{counts[2]/num_sims:.0%}",
                "4th": f"{counts[3]/num_sims:.0%}"
            })
        st.table(pd.DataFrame(group_data))

st.divider()

st.header("2. Knockout Stage Probabilities")
st.write("Percentage chance of reaching each round (cumulative). Sorted by chance of winning.")

all_teams = sorted([t for g, teams in groups.items() for t in teams])
rounds = ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final", "Winner"]

ko_table = []
for team in all_teams:
    if ko_counts[team].get("Round of 32", 0) > 0:
        row = {"Team": team}
        for r in rounds:
            row[r] = ko_counts[team].get(r, 0) / num_sims
        ko_table.append(row)
        
df_ko = pd.DataFrame(ko_table)
if not df_ko.empty:
    df_ko = df_ko.sort_values(by="Winner", ascending=False)
    st.dataframe(
        df_ko.style.format({r: "{:.1%}" for r in rounds}),
        use_container_width=True,
        height=600
    )
