"""Train the food freshness prediction model.

The model uses simple food handling signals so beginners can understand and
extend the machine learning pipeline easily.
"""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import pickle


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "ml" / "food_data.csv"
MODEL_PATH = BASE_DIR / "models" / "freshness_model.pkl"


def train_model():
    """Train and save a DecisionTreeClassifier for freshness prediction."""
    data = pd.read_csv(DATA_PATH)
    features = data[["storage_hours", "temperature", "humidity"]]
    labels = data["label"]

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    model = Pipeline(
        steps=[
            ("columns", ColumnTransformer([("numeric", "passthrough", features.columns)])),
            ("classifier", DecisionTreeClassifier(max_depth=4, random_state=42)),
        ]
    )
    model.fit(features, encoded_labels)

    MODEL_PATH.parent.mkdir(exist_ok=True)
    with MODEL_PATH.open("wb") as model_file:
        pickle.dump({"model": model, "label_encoder": label_encoder}, model_file)

    print(f"Freshness model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
