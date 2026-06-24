import os
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict
from tournament_config import GROUPS, KNOCKOUT_DEFS

# Use relative paths for the project structure so it works on both local and server
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MODEL_PATH = os.path.join(BASE_DIR, "poisson_model.pkl")
MATCHES_FILE = os.path.join(DATA_DIR, "wc_group_matches.txt")
REAL_RESULTS_FILE = os.path.join(DATA_DIR, "real_results.csv")

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
            parts = line.strip().split('\t')
            if len(parts) == 2:
                matches.append((parts[0].strip(), parts[1].strip()))
    return matches

def load_real_results():
    """Returns {(home_team, away_team): (home_goals, away_goals)} for completed matches."""
    results = {}
    if not os.path.exists(REAL_RESULTS_FILE):
        return results
    df = pd.read_csv(REAL_RESULTS_FILE, header=None,
                     names=['home_team', 'away_team', 'home_goal', 'away_goal'])
    df['home_goal'] = pd.to_numeric(df['home_goal'], errors='coerce')
    df['away_goal'] = pd.to_numeric(df['away_goal'], errors='coerce')
    df = df.dropna()
    for _, row in df.iterrows():
        results[(row['home_team'], row['away_team'])] = (int(row['home_goal']), int(row['away_goal']))
    return results

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

def simulate_group_stage(groups, matches, team_to_group, model, real_results=None):
    standings = {g: {t: {'pts': 0, 'gd': 0, 'gf': 0} for t in teams} for g, teams in groups.items()}
    match_results = []

    if real_results is None:
        real_results = {}

    for t1, t2 in matches:
        g = team_to_group.get(t1)
        if not g: continue

        if (t1, t2) in real_results:
            s1, s2 = real_results[(t1, t2)]
        else:
            s1, s2 = predict_score(t1, t2, model)
        match_results.append((t1, t2, s1, s2))
        
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
            
    # Build head-to-head results per group
    h2h = {}
    for t1, t2, s1, s2 in match_results:
        g = team_to_group[t1]
        if g not in h2h:
            h2h[g] = {}
        h2h[g][(t1, t2)] = (s1, s2)

    group_rankings = {}
    for g, table in standings.items():
        group_rankings[g] = _rank_group(table, h2h.get(g, {}))
    return standings, group_rankings, match_results


def _rank_group(table, h2h):
    """Rank group teams: pts > h2h pts > h2h gd > h2h gf > overall gd > overall gf."""

    def h2h_record(team, opponents):
        pts = gd = gf = 0
        for opp in opponents:
            if (team, opp) in h2h:
                st, so = h2h[(team, opp)]
            elif (opp, team) in h2h:
                so, st = h2h[(opp, team)]
            else:
                continue
            gf += st
            gd += st - so
            if st > so: pts += 3
            elif st == so: pts += 1
        return pts, gd, gf

    teams = list(table.keys())
    sorted_by_pts = sorted(teams, key=lambda t: table[t]['pts'], reverse=True)

    result = []
    i = 0
    while i < len(sorted_by_pts):
        pts_val = table[sorted_by_pts[i]]['pts']
        j = i + 1
        while j < len(sorted_by_pts) and table[sorted_by_pts[j]]['pts'] == pts_val:
            j += 1
        tied = sorted_by_pts[i:j]
        if len(tied) == 1:
            result.extend(tied)
        else:
            ranked = sorted(tied, key=lambda t: (
                *h2h_record(t, [x for x in tied if x != t]),
                table[t]['gd'],
                table[t]['gf']
            ), reverse=True)
            result.extend(ranked)
        i = j
    return result

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
    real_results = load_real_results()

    pos_counts = {g: {t: [0]*4 for t in teams} for g, teams in groups.items()}
    ko_counts = {t: defaultdict(int) for g, teams in groups.items() for t in teams}
    match_outcomes = defaultdict(lambda: [0, 0, 0])

    for _ in range(num_sims):
        standings, sim_rankings, results = simulate_group_stage(groups, matches, team_to_group, model, real_results)
        for g, ranked_teams in sim_rankings.items():
            for i, t in enumerate(ranked_teams):
                if i < 4: pos_counts[g][t][i] += 1

        for t1, t2, s1, s2 in results:
            if s1 > s2:
                match_outcomes[(t1, t2)][0] += 1
            elif s1 == s2:
                match_outcomes[(t1, t2)][1] += 1
            else:
                match_outcomes[(t1, t2)][2] += 1

        reached = simulate_knockout_stage(standings, sim_rankings, model)
        for (team, round_label) in reached:
            if team != "TBD": ko_counts[team][round_label] += 1
            
    return groups, pos_counts, ko_counts, match_outcomes
