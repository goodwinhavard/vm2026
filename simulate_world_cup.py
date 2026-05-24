import os
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict

# Use absolute paths for the project structure as provided in context
BASE_DIR = r"c:\projects\vm2026"
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(BASE_DIR, "poisson_model.pkl")
MATCHES_FILE = os.path.join(DATA_DIR, "wc_group_matches.txt")
GROUPS_FILE = os.path.join(DATA_DIR, "wc_groups.txt")

# Knockout definitions and source resolution logic adapted from tipping_knockout.py
KNOCKOUT_DEFS = {
    "Round of 32": {
        73: {"home": {"type": "group", "group": "Group A", "position": "runner_up"}, "away": {"type": "group", "group": "Group B", "position": "runner_up"}},
        74: {"home": {"type": "group", "group": "Group E", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group A", "Group B", "Group C", "Group D", "Group F"]}},
        75: {"home": {"type": "group", "group": "Group F", "position": "winner"}, "away": {"type": "group", "group": "Group C", "position": "runner_up"}},
        76: {"home": {"type": "group", "group": "Group C", "position": "winner"}, "away": {"type": "group", "group": "Group F", "position": "runner_up"}},
        77: {"home": {"type": "group", "group": "Group I", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group C", "Group D", "Group F", "Group G", "Group H"]}},
        78: {"home": {"type": "group", "group": "Group E", "position": "runner_up"}, "away": {"type": "group", "group": "Group I", "position": "runner_up"}},
        79: {"home": {"type": "group", "group": "Group A", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group C", "Group E", "Group F", "Group H", "Group I"]}},
        80: {"home": {"type": "group", "group": "Group L", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group E", "Group H", "Group I", "Group J", "Group K"]}},
        81: {"home": {"type": "group", "group": "Group D", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group B", "Group E", "Group F", "Group I", "Group J"]}},
        82: {"home": {"type": "group", "group": "Group G", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group A", "Group E", "Group H", "Group I", "Group J"]}},
        83: {"home": {"type": "group", "group": "Group K", "position": "runner_up"}, "away": {"type": "group", "group": "Group L", "position": "runner_up"}},
        84: {"home": {"type": "group", "group": "Group H", "position": "winner"}, "away": {"type": "group", "group": "Group J", "position": "runner_up"}},
        85: {"home": {"type": "group", "group": "Group B", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group E", "Group F", "Group G", "Group I", "Group J"]}},
        86: {"home": {"type": "group", "group": "Group J", "position": "winner"}, "away": {"type": "group", "group": "Group H", "position": "runner_up"}},
        87: {"home": {"type": "group", "group": "Group K", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group D", "Group E", "Group I", "Group J", "Group L"]}},
        88: {"home": {"type": "group", "group": "Group D", "position": "runner_up"}, "away": {"type": "group", "group": "Group G", "position": "runner_up"}},
    },
    "Round of 16": {
        89: {"home": {"type": "match", "match": 74}, "away": {"type": "match", "match": 77}},
        90: {"home": {"type": "match", "match": 73}, "away": {"type": "match", "match": 75}},
        91: {"home": {"type": "match", "match": 76}, "away": {"type": "match", "match": 78}},
        92: {"home": {"type": "match", "match": 79}, "away": {"type": "match", "match": 80}},
        93: {"home": {"type": "match", "match": 83}, "away": {"type": "match", "match": 84}},
        94: {"home": {"type": "match", "match": 81}, "away": {"type": "match", "match": 82}},
        95: {"home": {"type": "match", "match": 86}, "away": {"type": "match", "match": 88}},
        96: {"home": {"type": "match", "match": 85}, "away": {"type": "match", "match": 87}},
    },
    "Quarterfinals": {
        97: {"home": {"type": "match", "match": 89}, "away": {"type": "match", "match": 90}},
        98: {"home": {"type": "match", "match": 93}, "away": {"type": "match", "match": 94}},
        99: {"home": {"type": "match", "match": 91}, "away": {"type": "match", "match": 92}},
        100: {"home": {"type": "match", "match": 95}, "away": {"type": "match", "match": 96}},
    },
    "Semifinals": {
        101: {"home": {"type": "match", "match": 97}, "away": {"type": "match", "match": 98}},
        102: {"home": {"type": "match", "match": 99}, "away": {"type": "match", "match": 100}},
    },
    "Final": {
        104: {"home": {"type": "match", "match": 101}, "away": {"type": "match", "match": 102}},
    },
}

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
    groups = {}
    team_to_group = {}
    if not os.path.exists(GROUPS_FILE):
        raise FileNotFoundError(f"Groups file not found: {GROUPS_FILE}")
    
    with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            group_name, team_name = [part.strip() for part in line.split(":", 1)]
            groups.setdefault(group_name, []).append(team_name)
            team_to_group[team_name] = group_name
    return groups, team_to_group

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

def main():
    num_sims = 1000
    groups, pos_counts, ko_counts = run_full_simulation(num_sims)

    print(f"World Cup 2026 Group Stage Simulation ({num_sims} iterations)")
    print("Format: Team | Probabilities of finishing (1st, 2nd, 3rd, 4th)\n")
    for g in sorted(groups.keys()):
        print(f"--- {g} ---")
        # Sort teams by their probability of finishing at the top of the group
        sorted_teams = sorted(groups[g], key=lambda t: pos_counts[g][t], reverse=True)
        for i, t in enumerate(sorted_teams):
            probs = [f"{c/num_sims:.0%}" for c in pos_counts[g][t]]
            print(f"{i+1}. {t.ljust(20)}: {', '.join(probs)}")
        print()

    print("Knockout Stage Probabilities (Top 20 Favorites)")
    print("Team".ljust(20) + " | R32   | R16   | QF    | SF    | Final | Winner")
    print("-" * 75)
    all_teams = [t for g, teams in groups.items() for t in teams]
    sorted_overall = sorted(all_teams, key=lambda t: ko_counts[t]["Winner"], reverse=True)
    for t in sorted_overall[:20]:
        row = []
        for r in ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final", "Winner"]:
            prob = ko_counts[t].get(r, 0) / num_sims
            row.append(f"{prob:.1%}".ljust(5))
        print(f"{t.ljust(20)} | {' | '.join(row)}")
    

if __name__ == "__main__":
    main()