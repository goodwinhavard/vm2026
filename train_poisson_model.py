import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson
import os


def load_fifa_ranks(rank_file=None):
    """
    Load FIFA ranks from file. Teams not in file get rank 1000.
    Returns dict: team_name -> rank
    """
    ranks = {}
    if rank_file and os.path.exists(rank_file):
        with open(rank_file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    team, rank = parts
                    try:
                        ranks[team.strip()] = float(rank)
                    except ValueError:
                        pass
    return ranks


def train_poisson_model(matches_df, fifa_rank_file=None):
    """
    Fit a Poisson model on played matches with FIFA rank as optional covariate.
    Returns (model_dict, error_message). On success error_message is None.
    """
    df = matches_df.copy()
    df = df[df['Home Score'].astype(str).str.strip() != '']
    df = df[df['Away Score'].astype(str).str.strip() != '']
    df['Home Score'] = pd.to_numeric(df['Home Score'], errors='coerce')
    df['Away Score'] = pd.to_numeric(df['Away Score'], errors='coerce')
    df = df.dropna(subset=['Home Score', 'Away Score'])
    df[['Home Score', 'Away Score']] = df[['Home Score', 'Away Score']].astype(int)

    # normalize team names and ensure both home and away teams are included
    df['Home Team'] = df['Home Team'].astype(str).str.strip()
    df['Away Team'] = df['Away Team'].astype(str).str.strip()
    df = df.dropna(subset=['Home Team', 'Away Team'])
    teams    = sorted(pd.unique(df[['Home Team', 'Away Team']].values.ravel()))
    n        = len(teams)
    team_idx = {t: i for i, t in enumerate(teams)}
    # map to integer indices (ensure dtype=int to avoid indexing errors)
    home_idx   = df['Home Team'].map(team_idx).astype(int).values
    away_idx   = df['Away Team'].map(team_idx).astype(int).values
    home_goals = df['Home Score'].values
    away_goals = df['Away Score'].values

    # Load FIFA ranks if provided
    use_fifa_rank = fifa_rank_file is not None and os.path.exists(fifa_rank_file)
    team_ranks = None
    team_ranks_norm = None
    
    if use_fifa_rank:
        fifa_ranks_dict = load_fifa_ranks(fifa_rank_file)
        # Create normalized rank array: teams not in list get 1000, then normalize to mean 0
        team_ranks = np.array([fifa_ranks_dict.get(t, 1000) for t in teams], dtype=float)
        team_ranks_norm = (team_ranks - team_ranks.mean()) / team_ranks.std()  # standardize

    if use_fifa_rank:
        def unpack(params):
            home_adv = params[0]
            attack   = np.concatenate([[0.0], params[1:n]])
            defense  = params[n:2*n]
            beta_rank = params[2*n]
            return home_adv, attack, defense, beta_rank

        def neg_log_likelihood(params):
            home_adv, attack, defense, beta_rank = unpack(params)
            lam_home = np.exp(home_adv + attack[home_idx] + defense[away_idx] + 
                              beta_rank * team_ranks_norm[home_idx])
            lam_away = np.exp(           attack[away_idx] + defense[home_idx] + 
                              beta_rank * team_ranks_norm[away_idx])
            ll = (poisson.logpmf(home_goals, lam_home) +
                  poisson.logpmf(away_goals, lam_away))
            return -ll.sum()

        n_params = 1 + (n - 1) + n + 1  # home_adv + (n-1) attacks + n defenses + beta_rank
    else:
        def unpack(params):
            home_adv = params[0]
            attack   = np.concatenate([[0.0], params[1:n]])
            defense  = params[n:2*n]
            return home_adv, attack, defense

        def neg_log_likelihood(params):
            home_adv, attack, defense = unpack(params)
            lam_home = np.exp(home_adv + attack[home_idx] + defense[away_idx])
            lam_away = np.exp(           attack[away_idx] + defense[home_idx])
            ll = (poisson.logpmf(home_goals, lam_home) +
                  poisson.logpmf(away_goals, lam_away))
            return -ll.sum()

        n_params = 1 + (n - 1) + n  # home_adv + (n-1) attacks + n defenses

    x0       = np.zeros(n_params)
    result   = minimize(neg_log_likelihood, x0, method='L-BFGS-B',
                        options={'maxiter': 1000, 'ftol': 1e-12})

    if not (result.success or result.fun < neg_log_likelihood(x0)):
        return None, result.message

    if use_fifa_rank:
        home_adv, attack, defense, beta_rank = unpack(result.x)
    else:
        home_adv, attack, defense = unpack(result.x)
        beta_rank = None

    model = {
        'teams':         teams,
        'team_idx':      team_idx,
        'home_adv':      home_adv,
        'attack':        attack,
        'defense':       defense,
        'beta_rank':     beta_rank,
        'team_ranks':    team_ranks,
        'team_ranks_norm': team_ranks_norm,
        'n_params':      n_params,
        'n_matches':     len(df),
        'result':        result,
    }
    return model, None
