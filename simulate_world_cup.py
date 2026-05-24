import os
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict
from tournament_config import GROUPS, KNOCKOUT_DEFS

# Use relative paths for the project structure so it works on both local and server
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(BASE_DIR, "poisson_model.pkl")
MATCHES_FILE = os.path.join(DATA_DIR, "wc_group_matches.txt")

def resolve_source(source, standings, group_rankings, match_winners, used_thirds):
    if source["type"] == "group":
        group, pos = source["group"], source["position"]
        if pos == "winner": return group_rankings[group][0]
        if pos == "runner_up": return group_rankings[group][1]
    elif source["type"] == "best_third":
        third_places = []
        for g in source["groups"]:
            team = group_rankings[g][2]
            if team not in used_thirds:
                stats = standings[g][team]
                third_places.append((team, stats['pts'], stats['gd'], stats['gf']))
        if third_places:
            best = sorted(third_places, key=lambda x: (x[1], x[2], x[3]), reverse=True)[0]
            used_thirds.add(best[0]); return best[0]
    elif source["type"] == "match":
        return match_winners.get(source["match"], "TBD")
    return "TBD"

def get_match_winner(t1, t2, model):
    if t1 == "TBD" or t2 == "TBD": return "TBD"
    s1, s2 = predict_score(t1, t2, model)
    if s1 > s2: return t1
    if s2 > s1: return t2
    # Extra time simulation
    while s1 == s2:
        s1, s2 = predict_score(t1, t2, model)
    return t1 if s1 > s2 else t2

def load_poisson_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run train_model.py first.")
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def load_groups():
    team_to_group = {}
    for group_name, teams in GROUPS.items():
        for team in teams:
            team_to_group[team] = group_name
    return GROUPS, team_to_group

def load_matches():
    matches = []
    if not os.path.exists(MATCHES_FILE):
        raise FileNotFoundError(f"Matches file not found: {MATCHES_FILE}")
    with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            # Matches are tab-separated as per wc_group_matches.txt
            parts = line.strip().split('\t')
            if len(parts) == 2:
                matches.append((parts[0].strip(), parts[1].strip()))
    return matches

def predict_score(home_team, away_team, model):
    idx_h = model['team_idx'].get(home_team)
    idx_a = model['team_idx'].get(away_team)
    
    if idx_h is None or idx_a is None:
        # Fallback if a team wasn't in the training set
        return np.random.poisson(1.0), np.random.poisson(1.0)

    # Calculate log-lambdas using the Poisson model parameters
    # Note: The first team is treated as the 'home' team for home_adv purposes
    l_h_log = model['home_adv'] + model['attack'][idx_h] + model['defense'][idx_a]
    l_a_log = model['attack'][idx_a] + model['defense'][idx_h]
    
    # Add FIFA rank adjustment if the model was trained with it
    if model.get('beta_rank') is not None and model.get('team_ranks_norm') is not None:
        l_h_log += model['beta_rank'] * model['team_ranks_norm'][idx_h]
        l_a_log += model['beta_rank'] * model['team_ranks_norm'][idx_a]
        
    return np.random.poisson(np.exp(l_h_log)), np.random.poisson(np.exp(l_a_log))

def simulate_group_stage(groups, matches, team_to_group, model):
    # Initialize table stats for each team
    standings = {g: {t: {'pts': 0, 'gd': 0, 'gf': 0} for t in teams} for g, teams in groups.items()}
    
    for t1, t2 in matches:
        g = team_to_group.get(t1)
        if not g: continue
        
        s1, s2 = predict_score(t1, t2, model)
        
        standings[g][t1]['gf'] += s1
        standings[g][t1]['gd'] += (s1 - s2)
        standings[g][t2]['gf'] += s2
        standings[g][t2]['gd'] += (s2 - s1)
        
        if s1 > s2:
            standings[g][t1]['pts'] += 3
        elif s2 > s1:
            standings[g][t2]['pts'] += 3
        else:
            standings[g][t1]['pts'] += 1
            standings[g][t2]['pts'] += 1
            
    group_rankings = {}
    for g, table in standings.items():
        # Standard tie-breakers: Points, Goal Difference, Goals For
        sorted_teams = sorted(table.items(), key=lambda x: (x[1]['pts'], x[1]['gd'], x[1]['gf']), reverse=True)
        group_rankings[g] = [t for t, stats in sorted_teams]
    return standings, group_rankings

def simulate_knockout_stage(standings, group_rankings, model):
    match_winners, used_thirds, reached = {}, set(), []
    for round_name, round_matches in KNOCKOUT_DEFS.items():
        for match_num, match_def in round_matches.items():
            t1 = resolve_source(match_def["home"], standings, group_rankings, match_winners, used_thirds)
            t2 = resolve_source(match_def["away"], standings, group_rankings, match_winners, used_thirds)
            reached.extend([(t1, round_name), (t2, round_name)])
            winner = get_match_winner(t1, t2, model)
            match_winners[match_num] = winner
    if 104 in match_winners:
        reached.append((match_winners[104], "Winner"))
    return reached

def run_full_simulation(num_sims=1000, model=None):
    if model is None:
        model = load_poisson_model()
    groups, team_to_group = load_groups()
    matches = load_matches()

    # Track finishing positions for each team in each group
    pos_counts = {g: {t: [0]*4 for t in teams} for g, teams in groups.items()}
    ko_counts = {t: defaultdict(int) for g, teams in groups.items() for t in teams}

    for _ in range(num_sims):
        standings, sim_rankings = simulate_group_stage(groups, matches, team_to_group, model)
        for g, ranked_teams in sim_rankings.items():
            for i, t in enumerate(ranked_teams):
                if i < 4: pos_counts[g][t][i] += 1

        reached = simulate_knockout_stage(standings, sim_rankings, model)
        for (team, round_label) in reached:
            if team != "TBD": ko_counts[team][round_label] += 1
            
    return groups, pos_counts, ko_counts

# def main():
#     num_sims = 1000
#     groups, pos_counts, ko_counts = run_full_simulation(num_sims)

#     print(f"World Cup 2026 Group Stage Simulation ({num_sims} iterations)")
#     print("Format: Team | Probabilities of finishing (1st, 2nd, 3rd, 4th)\n")
#     for g in sorted(groups.keys()):
#         print(f"--- {g} ---")
#         # Sort teams by their probability of finishing at the top of the group
#         sorted_teams = sorted(groups[g], key=lambda t: pos_counts[g][t], reverse=True)
#         for i, t in enumerate(sorted_teams):
#             probs = [f"{c/num_sims:.0%}" for c in pos_counts[g][t]]
#             print(f"{i+1}. {t.ljust(20)}: {', '.join(probs)}")
#         print()

#     print("Knockout Stage Probabilities (Top 20 Favorites)")
#     print("Team".ljust(20) + " | R32   | R16   | QF    | SF    | Final | Winner")
#     print("-" * 75)
#     all_teams = [t for g, teams in groups.items() for t in teams]
#     sorted_overall = sorted(all_teams, key=lambda t: ko_counts[t]["Winner"], reverse=True)
#     for t in sorted_overall[:20]:
#         row = []
#         for r in ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final", "Winner"]:
#             prob = ko_counts[t].get(r, 0) / num_sims
#             row.append(f"{prob:.1%}".ljust(5))
#         print(f"{t.ljust(20)} | {' | '.join(row)}")
    

# if __name__ == "__main__":
#     main()