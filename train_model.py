import os
import pickle
import pandas as pd
from train_poisson_model import train_poisson_model


def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'training_data_fra_kvalikk_og_hist.csv')
    if not os.path.exists(csv_path):
        print(f"training CSV not found: {csv_path}")
        return
    df = pd.read_csv(csv_path)

    # Read random generated matches
    custom_path = os.path.join(os.path.dirname(__file__), 'data', 'custom_matches_manuell.csv')
    if os.path.exists(custom_path):
        custom_df = pd.read_csv(custom_path)

        # Align custom generated match columns with the training data schema
        custom_df = custom_df.rename(
            columns={
                'team1': 'home_team',
                'team2': 'away_team',
                'team1_goals': 'home_goal',
                'team2_goals': 'away_goal',
                'Home-Team': 'home_team',
                'Away-Team': 'away_team',
                'Home-Goals': 'home_goal',
                'Away-Goals': 'away_goal',
            }
        )

        expected_cols = ['home_team', 'away_team', 'home_goal', 'away_goal']
        if not set(expected_cols).issubset(custom_df.columns):
            missing = sorted(set(expected_cols) - set(custom_df.columns))
            raise ValueError(
                f"custom_matches.csv is missing required columns: {missing}"
            )

        custom_df = custom_df[expected_cols]
        df = pd.concat([df, custom_df], ignore_index=True, sort=False)
    else:
        print(f"custom_matches.csv not found: {custom_path}")

    #print(df.head())

    #exit(1)

    # Rename columns to match the trainer's expectations
    mapping = {
        'home_team': 'Home Team',
        'away_team': 'Away Team',
        'home_goal': 'Home Score',
        'away_goal': 'Away Score',
    }
    df = df.rename(columns=mapping)

    rank_file = os.path.join(os.path.dirname(__file__), 'data', 'fifa_rank.txt')
    model, err = train_poisson_model(df, fifa_rank_file=rank_file)
    if err:
        print('Training failed:', err)
        return

    out_path = os.path.join(os.path.dirname(__file__), 'poisson_model.pkl')
    with open(out_path, 'wb') as f:
        pickle.dump(model, f)

    print('Saved model to', out_path)
    print('Teams:', len(model['teams']))
    print('Home advantage:', model['home_adv'])
    print('FIFA Rank coefficient:', model['beta_rank'])
    # show top 5 attack strengths
    attacks = list(zip(model['teams'], model['attack']))
    defenses = list(zip(model['teams'], model['defense']))
    attacks.sort(key=lambda x: x[1], reverse=True)
    defenses.sort(key=lambda x: x[1])
    print('Top 5 attacks:', attacks[:5])
    print('Top 5 (weakest) defenses:', defenses[:5])


if __name__ == '__main__':
    main()
