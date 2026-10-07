import pandas as pd


def load_and_preprocess():

    df = pd.read_csv(
        "ml/datasets/training_data.csv"
    )

    difficulty_mapping = {
        "Easy": 0,
        "Medium": 1,
        "Hard": 2
    }

    df["difficulty"] = (
        df["difficulty"]
        .map(difficulty_mapping)
    )

    return df


if __name__ == "__main__":

    df = load_and_preprocess()

    print(df.head())