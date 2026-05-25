import streamlit as st
import pandas as pd
import os
from functions.train_poisson_model import train_poisson_model
from functions.simulate_world_cup import run_full_simulation


@st.cache_resource
def train_and_save_model():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'training_data_fra_kvalikk_og_hist.csv')
    if not os.path.exists(csv_path):
        return None, f"Training CSV not found: {csv_path}"

    df = pd.read_csv(csv_path)

    custom_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'custom_matches_manuell.csv')
    if os.path.exists(custom_path):
        custom_df = pd.read_csv(custom_path)

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

        n_real = len(df)
        n_syn = len(custom_df)
        total = n_real + n_syn

        df['Weight'] = 0.6
        custom_df['Weight'] = 0.4

        total_weight = df['Weight'].sum() + custom_df['Weight'].sum()
        df['Weight'] = df['Weight'] * (total / total_weight)
        custom_df['Weight'] = custom_df['Weight'] * (total / total_weight)

        df = pd.concat([df, custom_df], ignore_index=True, sort=False)

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
    groups, pos_counts, ko_counts, match_outcomes = run_full_simulation(num_sims, model=_model)
    ko_counts_clean = {team: dict(rounds) for team, rounds in ko_counts.items()}
    match_outcomes_clean = dict(match_outcomes)
    return groups, pos_counts, ko_counts_clean, match_outcomes_clean
