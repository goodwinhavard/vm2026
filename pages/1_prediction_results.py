import streamlit as st
import pandas as pd
from tournament_config import KNOCKOUT_DEFS

st.set_page_config(page_title="World Cup 2026 Simulation", layout="wide")

st.title("🏆 World Cup 2026 Predictions")
st.markdown("""
This page shows the probabilities of each team reaching various stages of the 2026 World Cup,
calculated using a Poisson-based prediction model trained on historical and qualifying data.
""")

num_sims = 100000

if "sim_results" not in st.session_state:
    st.warning("Please visit the **Home** page first to load the simulation results.")
    st.stop()

groups, pos_counts, ko_counts, match_outcomes, r32_outcomes = st.session_state["sim_results"]

all_teams_list = [team for group in groups.values() for team in group]

st.header("3. Round of 32 Predicted Matchups")
st.write("Top candidates for each slot in the Round of 32, ranked by group stage simulation probability.")

def slot_label(source):
    if isinstance(source, str):
        return source
    if source["type"] == "group":
        pos = "1st" if source["position"] == "winner" else "2nd"
        return f"{source['group']} ({pos})"
    elif source["type"] == "best_third":
        letters = "/".join(g.replace("Group ", "") for g in source["groups"])
        return f"Best 3rd from {letters}"
    return "TBD"

def top_candidates(source, top_n=3):
    if isinstance(source, str):
        return []
    if source["type"] == "group":
        group = source["group"]
        idx = 0 if source["position"] == "winner" else 1
        teams = [(t, pos_counts[group][t][idx] / num_sims) for t in pos_counts[group]]
    elif source["type"] == "best_third":
        teams = []
        for g in source["groups"]:
            for t in pos_counts[g]:
                teams.append((t, pos_counts[g][t][2] / num_sims))
    else:
        return []
    return sorted(teams, key=lambda x: -x[1])[:top_n]

def fmt_candidates(cands):
    return " / ".join(f"{t} ({p:.0%})" for t, p in cands)

r32_rows = []
for match_num in sorted(KNOCKOUT_DEFS["Round of 32"]):
    match_def = KNOCKOUT_DEFS["Round of 32"][match_num]
    home, away = match_def["home"], match_def["away"]
    home_label = slot_label(home)
    away_label = slot_label(away)
    home_cands = fmt_candidates(top_candidates(home))
    away_cands = fmt_candidates(top_candidates(away))
    outcomes = r32_outcomes.get(match_num, [0, 0])
    total = outcomes[0] + outcomes[1]
    home_pct = outcomes[0] / total if total > 0 else 0.5
    away_pct = outcomes[1] / total if total > 0 else 0.5
    row = {
        "Home": home_label,
        "Home Win%": home_pct,
        "Away Win%": away_pct,
        "Away": away_label,
    }
    if home_cands:
        row["Home top candidates"] = home_cands
    if away_cands:
        row["Away top candidates"] = away_cands
    r32_rows.append(row)

df_r32 = pd.DataFrame(r32_rows)
st.dataframe(
    df_r32.style.format({"Home Win%": "{:.1%}", "Away Win%": "{:.1%}"}),
    use_container_width=True,
    hide_index=True
)

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

st.header("4. Group Match Probabilities")
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


st.divider()

st.header("Group Stage Probabilities")
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
