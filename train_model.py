import os
import pickle
import pandas as pd
from train_poisson_model import train_poisson_model


def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'training_data.csv')
    if not os.path.exists(csv_path):
        print(f"training CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Rename columns to match the trainer's expectations
    mapping = {
        'home_team': 'Home Team',
        'away_team': 'Away Team',
        'home_goal': 'Home Score',
        'away_goal': 'Away Score',
    }
    df = df.rename(columns=mapping)

    rank_file = os.path.join(os.path.dirname(__file__), 'fifa_rank.txt')
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
