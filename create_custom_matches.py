import os
import pandas as pd
import numpy as np
from numpy.random import poisson
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Read FIFA ranking and team ratings
teams_data = []
with open(os.path.join(DATA_DIR, 'fifa_rank.txt'), 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            team, rank = parts
            teams_data.append({'team': team, 'rank': int(rank)})

teams_df = pd.DataFrame(teams_data)

# Find min and max ranks to normalize
min_rank = teams_df['rank'].min()
max_rank = teams_df['rank'].max()

# Normalize ranks to lambda values between 1 and 1.8
# Better rank (higher score) -> higher lambda
teams_df['lambda'] = 1 + (teams_df['rank'] - min_rank) / (max_rank - min_rank) * (1.5 - 1)

print(f"Teams loaded: {len(teams_df)}")
print(f"\nRank range: {min_rank} to {max_rank}")
print(f"Lambda range: {teams_df['lambda'].min():.3f} to {teams_df['lambda'].max():.3f}")
print(f"\nBest team: {teams_df.loc[teams_df['lambda'].idxmax(), 'team']} (lambda={teams_df['lambda'].max():.3f})")
print(f"Worst team: {teams_df.loc[teams_df['lambda'].idxmin(), 'team']} (lambda={teams_df['lambda'].min():.3f})")

# Create 100 custom matches with random teams
matches = []
np.random.seed(42)
random.seed(42)

team_list = teams_df.to_dict('records')

for i in range(500):
    # Randomly select two teams
    team1, team2 = random.sample(team_list, 2)
    
    # Draw goals from Poisson distribution using lambda based on team rank
    goals1 = poisson(team1['lambda'])
    goals2 = poisson(team2['lambda'])
    
    matches.append({
        'match_id': i + 1,
        'team1': team1['team'],
        'team1_rank': team1['rank'],
        'team1_lambda': team1['lambda'],
        'team1_goals': goals1,
        'team2': team2['team'],
        'team2_rank': team2['rank'],
        'team2_lambda': team2['lambda'],
        'team2_goals': goals2,
        'result': 'win' if goals1 > goals2 else ('draw' if goals1 == goals2 else 'loss')
    })

# Create matches dataframe
matches_df = pd.DataFrame(matches)

# Save to CSV
output_path = os.path.join(DATA_DIR, 'custom_matches.csv')
matches_df.to_csv(output_path, index=False)

print(f"\n{len(matches_df)} custom matches created and saved to '{output_path}'")
print(f"\nFirst 10 matches:")
print(matches_df.head(10).to_string())

# Summary statistics
print(f"\n\nMatch summary:")
print(f"Total matches: {len(matches_df)}")
print(f"Average goals per team: {matches_df[['team1_goals', 'team2_goals']].mean().mean():.2f}")
print(f"Average goals team1: {matches_df['team1_goals'].mean():.2f}")
print(f"Average goals team2: {matches_df['team2_goals'].mean():.2f}")

# Display clean results table
print(f"\n\nAll matches (Home-Team, Away-Team, Home-Goals, Away-Goals):")
results_table = matches_df[['team1', 'team2', 'team1_goals', 'team2_goals']].copy()
results_table.columns = ['Home-Team', 'Away-Team', 'Home-Goals', 'Away-Goals']
print(results_table.to_string(index=False))

results_table.to_csv(output_path, index=False)

