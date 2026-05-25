import streamlit as st
import pandas as pd
import numpy as np
import os
from functions.train_poisson_model import train_poisson_model
from functions.simulate_world_cup import run_full_simulation

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
            return None, f"custom_matches_manuell.csv is missing required columns: {missing}"
        
        custom_df = custom_df[expected_cols]
        
        # Calculate weights for 70% real / 30% synthetic split
        n_real = len(df)
        n_syn = len(custom_df)
        total = n_real + n_syn
        
        df['Weight'] = 0.4
        custom_df['Weight'] = 0.6#(0.5 * total) / n_syn

        # Normalize weights so they sum to the total number of matches
        total_weight = df['Weight'].sum() + custom_df['Weight'].sum()
        df['Weight'] = df['Weight'] * (total / total_weight)
        custom_df['Weight'] = custom_df['Weight'] * (total / total_weight)
                

        df = pd.concat([df, custom_df], ignore_index=True, sort=False)
        #df = custom_df
    
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

@st.cache_data
def get_simulation_results(num_sims, _model):
    """Run the simulation and cache the results."""
    groups, pos_counts, ko_counts, match_outcomes = run_full_simulation(num_sims, model=_model)
    # Convert defaultdicts to standard dicts for clean caching serialization
    ko_counts_clean = {team: dict(rounds) for team, rounds in ko_counts.items()}
    match_outcomes_clean = dict(match_outcomes)
    return groups, pos_counts, ko_counts_clean, match_outcomes_clean

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
    
#st.success(f"✓ Model trained on {len(model['teams'])} teams")

num_sims = 10000


with st.spinner(f"Running {num_sims} tournament simulations..."):
    groups, pos_counts, ko_counts, match_outcomes = get_simulation_results(num_sims, model)
    
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

st.divider()
st.header("3. Group Match Probabilities")
st.write("Outcome probabilities for all 72 group stage matches based on the simulation.")

# Filter by team
team_options = ["All teams"] + sorted(all_teams_list)
selected_team = st.selectbox("Filter matches by team:", options=team_options)

match_data = []
for (t1, t2), counts in match_outcomes.items():
    if selected_team == "All teams" or t1 == selected_team or t2 == selected_team:
        match_data.append({
            "Home Team": t1,
            "Away Team": t2,
            "Home Win %": counts[0] / num_sims,
            "Draw %": counts[1] / num_sims,
            "Away Win %": counts[2] / num_sims
        })

if match_data:
    df_display = pd.DataFrame(match_data)
    st.dataframe(
        df_display.style.format({
            "Home Win %": "{:.1%}",
            "Draw %": "{:.1%}",
            "Away Win %": "{:.1%}"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No matches found for the selected team.")
