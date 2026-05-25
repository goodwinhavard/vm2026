import streamlit as st

st.set_page_config(page_title="Methodology - World Cup 2026", layout="wide")

st.title("Methodology & Mathematical Framework")

st.markdown("""
This page explains the underlying logic, data sources, and mathematical models used to predict the outcomes of the FIFA World Cup 2026.

## 1. Data Usage
The model is trained on a combination of historical performance and current form:

*   **Historical Results:** International match data from 2018 onwards to establish a baseline for team strengths.
*   **2026 Qualifying Data:** Recent results from the ongoing 2026 World Cup qualification cycles across all confederations.
*   **Synthetic Normalization:** A small set of matches based on FIFA rankings is used to ensure the model converges for teams with limited recent match history.
*   **World Cup Games 2026:** As the tournament progresses, results from the 2026 World Cup matches are incorporated to update predictions in real-time.            


## 2. How the Simulation Works
Since a tournament's outcome depends on its specific bracket logic, we use a **Monte Carlo Simulation** approach:

1.  **Iteration:** We run the entire World Cup tournament 10,000 times.
2.  **Match Simulation:** For every individual match, we draw a random score from the calculated Poisson distributions for both teams.
3.  **Group Stage:** We simulate all group matches, calculate standings based on points, goal difference, and goals scored, and determine the ranking within the 12 groups.
4.  **Knockout Logic:** The simulation identifies the top two teams from each group and the eight best third-placed teams to fill the **Round of 32**.
5.  **Extra Time:** In knockout rounds, if a simulated match ends in a draw, we continue simulating until a winner is determined (representing extra time and penalties).
6.  **Probability Aggregation:** The final percentages shown on the results page represent the frequency with which each team reached a specific round across all 10,000 iterations.
""")

st.markdown("## 3. Mathematical Model")
st.markdown("### Bivariate Poisson Regression for Football")
st.markdown(
    "Goals scored in a football match are modelled as independent Poisson random variables. "
    "For a match between home team $h$ and away team $a$:"
)
st.latex(r"Y_h \sim \text{Poisson}(\lambda_h), \qquad Y_a \sim \text{Poisson}(\lambda_a)")
st.markdown("The expected goals are linked to team-specific parameters via a **log-linear model**:")
st.latex(r"""
\log \lambda_h = \mu + \alpha_h + \delta_a \\
\log \lambda_a = \alpha_a + \delta_h
""")
st.markdown("""
| Symbol | Meaning |
|--------|---------|
| $\\mu$ | Home advantage (shared across all matches) |
| $\\alpha_i$ | Attack strength of team $i$ — higher means more goals scored |
| $\\delta_i$ | Defensive strength of team $i$ — lower means fewer goals conceded |
""")

st.markdown("---")
st.markdown("### Identifiability Constraint")
st.markdown(
    "The model is over-parameterised without a constraint. "
    "We fix the attack parameter of the first team (alphabetically) to zero:"
)
st.latex(r"\alpha_0 = 0")
st.markdown("This makes all other attack parameters relative to that reference team.")

st.markdown("---")
st.markdown("### Parameter Estimation")
st.markdown(
    r"Parameters $\boldsymbol{\theta} = (\mu,\, \alpha_1, \dots, \alpha_{N-1},\, \delta_0, \dots, \delta_{N-1})$ "
    r"are estimated by **maximum likelihood**. The log-likelihood over $M$ matches is:"
)
st.latex(
    r"\ell(\boldsymbol{\theta}) = \sum_{m=1}^{M} \Bigl["
    r"\log p\!\left(y_h^{(m)} \mid \lambda_h^{(m)}\right)"
    r"+ \log p\!\left(y_a^{(m)} \mid \lambda_a^{(m)}\right)"
    r"\Bigr]"
)
st.markdown(
    r"where $\log p(k \mid \lambda) = k \log \lambda - \lambda - \log k!$ is the Poisson log-PMF. "
    "Optimisation is performed with **L-BFGS-B** (a quasi-Newton gradient method)."
)

st.markdown("---")
st.markdown("### Prediction")
st.markdown(
    r"For an unseen match $(h, a)$, the fitted $\hat{\lambda}_h$ and $\hat{\lambda}_a$ define full "
    "goal distributions. Match outcomes are simulated by drawing:"
)
st.latex(r"\tilde{Y}_h \sim \text{Poisson}(\hat{\lambda}_h), \qquad \tilde{Y}_a \sim \text{Poisson}(\hat{\lambda}_a)")
st.markdown(
    "Running many such draws gives a probability distribution over scorelines, and from "
    "that: win/draw/loss probabilities, expected goals, and more."
)

st.divider()
st.caption("Model developed by Håvard Goodwin | Framework: Scipy, Pandas, Streamlit")
