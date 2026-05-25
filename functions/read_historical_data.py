import pandas as pd
import numpy as np
import os
import kagglehub

# Download latest version
path = kagglehub.dataset_download("joshfjelstul/world-cup-database")

print("Path to dataset files:", path)


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

matches_csv = os.path.join(path, "matches.csv")
vm_historical_matches_df = pd.read_csv(matches_csv)

# Only include historical matches from 2018 and later
vm_historical_matches_df['match_date'] = pd.to_datetime(
    vm_historical_matches_df['match_date'], errors='coerce'
)
vm_historical_matches_df = vm_historical_matches_df[
    vm_historical_matches_df['match_date'].dt.year >= 2018
]


vm_historical_matches_df[['home_team', 'away_team']] = vm_historical_matches_df['match_name'].str.extract(r'^(.*?)\s+v\s+(.*?)$')
vm_historical_matches_df[['home_goal', 'away_goal']] = vm_historical_matches_df['score'].str.extract(r'^(\d+)[\u2013-](\d+)$').astype(int)

vm_historical_matches_df = vm_historical_matches_df[['home_team', 'away_team', 'home_goal', 'away_goal']]

vm_historical_matches_df[['home_team', 'away_team']] = vm_historical_matches_df[['home_team', 'away_team']].replace(
    {'East Germany': 'Germany', 'West Germany': 'Germany', 'Czech Republic': 'Czechia'}
)


# Leser inn kvalikkdata (hentet manuelt)
vm_kvalikk_2026 = pd.read_csv(os.path.join(DATA_DIR, "vm_kvalikk.csv"), header=0)
vm_kvalikk_2026.columns = vm_kvalikk_2026.columns.str.strip()
vm_kvalikk_2026 = vm_kvalikk_2026[['home_team', 'away_team', 'home_goal', 'away_goal']]
print(vm_kvalikk_2026.head())

combined_df = pd.concat([vm_historical_matches_df, vm_kvalikk_2026], ignore_index=True, sort=False)
print("Combined dataset shape:", combined_df.shape)
print(combined_df.head())

fifa_rank_path = os.path.join(DATA_DIR, "fifa_rank.txt")
wc_teams_rank_df = pd.read_csv(fifa_rank_path, sep='\t', header=None, encoding='utf-8')
wc_teams_2026 = wc_teams_rank_df[0].str.strip().tolist()

print("World Cup 2026 teams:", wc_teams_2026)

sub_version = combined_df[
    combined_df['home_team'].isin(wc_teams_2026)
    & combined_df['away_team'].isin(wc_teams_2026)
].reset_index(drop=True)
print("Filtered sub_version shape:", sub_version.shape)
print(len(sub_version))
print(sub_version.head())

sub_version.to_csv(os.path.join(DATA_DIR, "training_data_fra_kvalikk_og_hist.csv"), index=False)
