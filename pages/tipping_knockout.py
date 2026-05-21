import itertools
from pathlib import Path

import pandas as pd
import streamlit as st

# Import from tipping_group to get standings
import sys
sys.path.append(str(Path(__file__).resolve().parent))
from tipping_group import load_groups, build_matches, compute_standings, init_session_state


def get_winner(group, standings):
    """Get the winner (1st place) of a group."""
    return standings[group].iloc[0]["Team"]


def get_runner_up(group, standings):
    """Get the runner-up (2nd place) of a group."""
    return standings[group].iloc[1]["Team"]


def get_third_place(group, standings):
    """Get the 3rd place team of a group."""
    return standings[group].iloc[2]["Team"]


def get_best_third_place(groups_list, standings):
    """Get the best 3rd place team from a list of groups."""
    third_places = [
        (group, standings[group].iloc[2]["Pts"], standings[group].iloc[2]["GD"], standings[group].iloc[2]["GF"])
        for group in groups_list
        if group in standings and len(standings[group]) >= 3
    ]
    if third_places:
        best = sorted(third_places, key=lambda x: (x[1], x[2], x[3]), reverse=True)[0]
        return standings[best[0]].iloc[2]["Team"]
    return "TBD"


KNOCKOUT_DEFS = {
    "Round of 32": {
        73: {
            "home": {"type": "group", "group": "Group A", "position": "runner_up"},
            "away": {"type": "group", "group": "Group B", "position": "runner_up"},
            "label": "Runner-up A vs Runner-up B",
        },
        74: {
            "home": {"type": "group", "group": "Group E", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group A", "Group B", "Group C", "Group D", "Group F"]},
            "label": "Winner E vs Best 3rd A/B/C/D/F",
        },
        75: {
            "home": {"type": "group", "group": "Group F", "position": "winner"},
            "away": {"type": "group", "group": "Group C", "position": "runner_up"},
            "label": "Winner F vs Runner-up C",
        },
        76: {
            "home": {"type": "group", "group": "Group C", "position": "winner"},
            "away": {"type": "group", "group": "Group F", "position": "runner_up"},
            "label": "Winner C vs Runner-up F",
        },
        77: {
            "home": {"type": "group", "group": "Group I", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group C", "Group D", "Group F", "Group G", "Group H"]},
            "label": "Winner I vs Best 3rd C/D/F/G/H",
        },
        78: {
            "home": {"type": "group", "group": "Group E", "position": "runner_up"},
            "away": {"type": "group", "group": "Group I", "position": "runner_up"},
            "label": "Runner-up E vs Runner-up I",
        },
        79: {
            "home": {"type": "group", "group": "Group A", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group C", "Group E", "Group F", "Group H", "Group I"]},
            "label": "Winner A vs Best 3rd C/E/F/H/I",
        },
        80: {
            "home": {"type": "group", "group": "Group L", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group E", "Group H", "Group I", "Group J", "Group K"]},
            "label": "Winner L vs Best 3rd E/H/I/J/K",
        },
        81: {
            "home": {"type": "group", "group": "Group D", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group B", "Group E", "Group F", "Group I", "Group J"]},
            "label": "Winner D vs Best 3rd B/E/F/I/J",
        },
        82: {
            "home": {"type": "group", "group": "Group G", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group A", "Group E", "Group H", "Group I", "Group J"]},
            "label": "Winner G vs Best 3rd A/E/H/I/J",
        },
        83: {
            "home": {"type": "group", "group": "Group K", "position": "runner_up"},
            "away": {"type": "group", "group": "Group L", "position": "runner_up"},
            "label": "Runner-up K vs Runner-up L",
        },
        84: {
            "home": {"type": "group", "group": "Group H", "position": "winner"},
            "away": {"type": "group", "group": "Group J", "position": "runner_up"},
            "label": "Winner H vs Runner-up J",
        },
        85: {
            "home": {"type": "group", "group": "Group B", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group E", "Group F", "Group G", "Group I", "Group J"]},
            "label": "Winner B vs Best 3rd E/F/G/I/J",
        },
        86: {
            "home": {"type": "group", "group": "Group J", "position": "winner"},
            "away": {"type": "group", "group": "Group H", "position": "runner_up"},
            "label": "Winner J vs Runner-up H",
        },
        87: {
            "home": {"type": "group", "group": "Group K", "position": "winner"},
            "away": {"type": "best_third", "groups": ["Group D", "Group E", "Group I", "Group J", "Group L"]},
            "label": "Winner K vs Best 3rd D/E/I/J/L",
        },
        88: {
            "home": {"type": "group", "group": "Group D", "position": "runner_up"},
            "away": {"type": "group", "group": "Group G", "position": "runner_up"},
            "label": "Runner-up D vs Runner-up G",
        },
    },
    "Round of 16": {
        89: {
            "home": {"type": "match", "match": 74},
            "away": {"type": "match", "match": 77},
            "label": "Winner Match 74 vs Winner Match 77",
        },
        90: {
            "home": {"type": "match", "match": 73},
            "away": {"type": "match", "match": 75},
            "label": "Winner Match 73 vs Winner Match 75",
        },
        91: {
            "home": {"type": "match", "match": 76},
            "away": {"type": "match", "match": 78},
            "label": "Winner Match 76 vs Winner Match 78",
        },
        92: {
            "home": {"type": "match", "match": 79},
            "away": {"type": "match", "match": 80},
            "label": "Winner Match 79 vs Winner Match 80",
        },
        93: {
            "home": {"type": "match", "match": 83},
            "away": {"type": "match", "match": 84},
            "label": "Winner Match 83 vs Winner Match 84",
        },
        94: {
            "home": {"type": "match", "match": 81},
            "away": {"type": "match", "match": 82},
            "label": "Winner Match 81 vs Winner Match 82",
        },
        95: {
            "home": {"type": "match", "match": 86},
            "away": {"type": "match", "match": 88},
            "label": "Winner Match 86 vs Winner Match 88",
        },
        96: {
            "home": {"type": "match", "match": 85},
            "away": {"type": "match", "match": 87},
            "label": "Winner Match 85 vs Winner Match 87",
        },
    },
    "Quarterfinals": {
        97: {
            "home": {"type": "match", "match": 89},
            "away": {"type": "match", "match": 90},
            "label": "Winner Match 89 vs Winner Match 90",
        },
        98: {
            "home": {"type": "match", "match": 93},
            "away": {"type": "match", "match": 94},
            "label": "Winner Match 93 vs Winner Match 94",
        },
        99: {
            "home": {"type": "match", "match": 91},
            "away": {"type": "match", "match": 92},
            "label": "Winner Match 91 vs Winner Match 92",
        },
        100: {
            "home": {"type": "match", "match": 95},
            "away": {"type": "match", "match": 96},
            "label": "Winner Match 95 vs Winner Match 96",
        },
    },
    "Semifinals": {
        101: {
            "home": {"type": "match", "match": 97},
            "away": {"type": "match", "match": 98},
            "label": "Winner Match 97 vs Winner Match 98",
        },
        102: {
            "home": {"type": "match", "match": 99},
            "away": {"type": "match", "match": 100},
            "label": "Winner Match 99 vs Winner Match 100",
        },
    },
    "Final": {
        104: {
            "home": {"type": "match", "match": 101},
            "away": {"type": "match", "match": 102},
            "label": "Winner Match 101 vs Winner Match 102",
        },
    },
}


def resolve_best_third_place(groups_list, standings):
    third_places = [
        (group, standings[group].iloc[2]["Pts"], standings[group].iloc[2]["GD"], standings[group].iloc[2]["GF"])
        for group in groups_list
        if group in standings and len(standings[group]) >= 3
    ]
    if third_places:
        best = sorted(third_places, key=lambda x: (x[1], x[2], x[3]), reverse=True)[0]
        return standings[best[0]].iloc[2]["Team"]
    return "TBD"


def resolve_source(source, standings, results):
    if source["type"] == "group":
        group = source["group"]
        position = source["position"]
        if group not in standings:
            return "TBD"
        if position == "winner":
            return standings[group].iloc[0]["Team"]
        if position == "runner_up":
            return standings[group].iloc[1]["Team"]
        if position == "third":
            return standings[group].iloc[2]["Team"]
    if source["type"] == "best_third":
        return resolve_best_third_place(source["groups"], standings)
    if source["type"] == "match":
        return results.get(source["match"], "TBD")
    return "TBD"


def get_match_winner(score1, score2, team1, team2):
    if score1 is None or score2 is None or team1 == "TBD" or team2 == "TBD":
        return "TBD"
    if score1 > score2:
        return team1
    if score2 > score1:
        return team2
    return "TBD"


def knockout_input_key(round_name, match_num, score_index):
    safe_round = round_name.replace(" ", "_").lower()
    return f"knockout_{safe_round}_{match_num}_score{score_index}"


def build_knockout_results():
    results = {}
    for round_name, round_matches in KNOCKOUT_DEFS.items():
        for match_num in round_matches:
            score1 = st.session_state.get(knockout_input_key(round_name, match_num, 1), 0)
            score2 = st.session_state.get(knockout_input_key(round_name, match_num, 2), 0)
            results[match_num] = (score1, score2)
    return results


def compute_knockout_winners(standings):
    winners = {}
    round_results = build_knockout_results()
    for round_name, round_matches in KNOCKOUT_DEFS.items():
        for match_num, match_def in round_matches.items():
            team1 = resolve_source(match_def["home"], standings, winners)
            team2 = resolve_source(match_def["away"], standings, winners)
            score1 = st.session_state.get(knockout_input_key(round_name, match_num, 1), 0)
            score2 = st.session_state.get(knockout_input_key(round_name, match_num, 2), 0)
            winners[match_num] = get_match_winner(score1, score2, team1, team2)
    return winners


def display_knockout_matches(standings, winners):
    st.subheader("Knockout Stage")
    st.write("Enter match predictions below. Winners advance through the bracket.")

    for round_name, round_matches in KNOCKOUT_DEFS.items():
        st.markdown(f"### {round_name}")
        for match_num, match_def in round_matches.items():
            team1 = resolve_source(match_def["home"], standings, winners)
            team2 = resolve_source(match_def["away"], standings, winners)
            cols = st.columns([2, 1, 0.5, 1, 2])
            cols[0].write(f"{team1}")
            cols[1].number_input(
                f"Match {match_num}: {team1} score",
                min_value=0,
                max_value=20,
                key=knockout_input_key(round_name, match_num, 1),
                label_visibility="collapsed",
            )
            cols[2].write(":")
            cols[3].number_input(
                f"Match {match_num}: {team2} score",
                min_value=0,
                max_value=20,
                key=knockout_input_key(round_name, match_num, 2),
                label_visibility="collapsed",
            )
            cols[4].write(f"{team2}")
            #st.caption(f"Match {match_num} - {match_def['label']}")


def main():
    st.title("Knockout Stage")
    st.header("World Cup 2026 - Knockout Tournament")

    init_session_state()

    groups = load_groups()
    matches = build_matches(groups)
    standings = compute_standings(groups, matches)
    st.session_state.group_standings = standings

    winners = compute_knockout_winners(standings)
    display_knockout_matches(standings, winners)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
