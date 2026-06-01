import streamlit as st
import pandas as pd
import os
from functions.train_poisson_model import train_poisson_model
from functions.simulate_world_cup import run_full_simulation
from config import WEIGHT_HISTORICAL, WEIGHT_CUSTOM_MANUAL, WEIGHT_EXTRA_MATCHES


@st.cache_resource
def train_and_save_model():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'training_data_fra_kvalikk_og_hist.csv')
    if not os.path.exists(csv_path):
        return None, f"Training CSV not found: {csv_path}"

    df = pd.read_csv(csv_path)
    df['Weight'] = WEIGHT_HISTORICAL

    extra_dfs = [df]

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
        custom_df['Weight'] = WEIGHT_CUSTOM_MANUAL
        extra_dfs.append(custom_df)

    extra_matches_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'extra_matches.csv')
    if os.path.exists(extra_matches_path):
        extra_df = pd.read_csv(
            extra_matches_path,
            header=None,
            names=['home_team', 'away_team', 'home_goal', 'away_goal'],
        )
        extra_df['home_goal'] = pd.to_numeric(extra_df['home_goal'], errors='coerce')
        extra_df['away_goal'] = pd.to_numeric(extra_df['away_goal'], errors='coerce')
        extra_df = extra_df.dropna(subset=['home_goal', 'away_goal'])
        extra_df['Weight'] = WEIGHT_EXTRA_MATCHES
        extra_dfs.append(extra_df)

    if len(extra_dfs) > 1:
        df = pd.concat(extra_dfs, ignore_index=True, sort=False)
        total_weight = df['Weight'].sum()
        df['Weight'] = df['Weight'] * (len(df) / total_weight)

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
