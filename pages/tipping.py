import itertools
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).resolve().parents[1] / "wc_groups.txt"


@st.cache_data
def load_groups():
    groups = {}
    text = DATA_FILE.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue

        group, team = [part.strip() for part in line.split(":", 1)]
        groups.setdefault(group, []).append(team)

    return {group: sorted(teams) for group, teams in sorted(groups.items())}


@st.cache_data
def build_matches(groups):
    return {group: list(itertools.combinations(teams, 2)) for group, teams in groups.items()}


def compute_standings(groups, matches):
    standings = {}
    for group, teams in groups.items():
        table = {
            team: {
                "Pld": 0,
                "W": 0,
                "D": 0,
                "L": 0,
                "GF": 0,
                "GA": 0,
                "GD": 0,
                "Pts": 0,
            }
            for team in teams
        }

        for team1, team2 in matches[group]:
            key1 = f"{group}_{team1}_vs_{team2}_score1"
            key2 = f"{group}_{team1}_vs_{team2}_score2"
            score1 = st.session_state.get(key1, 0)
            score2 = st.session_state.get(key2, 0)

            table[team1]["Pld"] += 1
            table[team2]["Pld"] += 1
            table[team1]["GF"] += score1
            table[team1]["GA"] += score2
            table[team2]["GF"] += score2
            table[team2]["GA"] += score1

            if score1 > score2:
                table[team1]["W"] += 1
                table[team2]["L"] += 1
                table[team1]["Pts"] += 3
            elif score1 < score2:
                table[team2]["W"] += 1
                table[team1]["L"] += 1
                table[team2]["Pts"] += 3
            else:
                table[team1]["D"] += 1
                table[team2]["D"] += 1
                table[team1]["Pts"] += 1
                table[team2]["Pts"] += 1

        for team in table:
            table[team]["GD"] = table[team]["GF"] - table[team]["GA"]

        standings[group] = pd.DataFrame(table).T.reset_index().rename(columns={"index": "Team"})
        standings[group] = standings[group].sort_values(
            by=["Pts", "GD", "GF", "Team"],
            ascending=[False, False, False, True],
        )

    return standings


def display_matches(groups, matches, standings):
    st.write(
        "Enter predictions for each group stage match below. Each team plays the other teams in its group once, "
        "for a total of 6 matches per group."
    )

    for group, fixtures in matches.items():
        with st.expander(f"{group} matches", expanded=True):
            for team1, team2 in fixtures:
                cols = st.columns([2, 1, 0.5, 1, 2])
                cols[0].write(f"**{team1}**")
                score1 = cols[1].number_input(
                    "",
                    min_value=0,
                    max_value=20,
                    key=f"{group}_{team1}_vs_{team2}_score1",
                    label_visibility="collapsed",
                )
                cols[2].write(":")
                score2 = cols[3].number_input(
                    "",
                    min_value=0,
                    max_value=20,
                    key=f"{group}_{team1}_vs_{team2}_score2",
                    label_visibility="collapsed",
                )
                cols[4].write(f"**{team2}**")

            st.markdown("---")
            st.write(f"### {group} standings")
            st.dataframe(standings[group], use_container_width=True)


def main():
    st.title("Tipping Page")
    st.header("World Cup 2026 Predictions")

    groups = load_groups()
    matches = build_matches(groups)
    standings = compute_standings(groups, matches)

    with st.form("prediction_form"):
        display_matches(groups, matches, standings)
        st.form_submit_button("Update standings")


if __name__ == "__main__":
    main()
