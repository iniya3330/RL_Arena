"""Decision Tree controller for CogniCare's adaptive question engine.

The model predicts a suitable next difficulty from engagement signals.
The training data is synthetic demonstration data and is NOT clinical data.
"""
from pathlib import Path
import pickle
import random
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

FEATURES = [
    "recent_accuracy",
    "avg_response_seconds",
    "hints_used",
    "current_difficulty",
    "correct_streak",
]
MODEL_DIR = Path(__file__).resolve().parent / "ml_models"
MODEL_PATH = MODEL_DIR / "decision_tree.pkl"
DATA_PATH = MODEL_DIR / "training_data.csv"


def generate_training_data(n=360, seed=42):
    """Generate transparent synthetic training examples for the demo."""
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        current = rng.randint(1, 3)
        accuracy = round(rng.uniform(0.15, 1.0), 2)
        response = round(rng.uniform(2.5, 32.0), 1)
        hints = rng.randint(0, 3)
        streak = rng.randint(0, 5)

        # Demonstration policy used to label synthetic examples.
        if accuracy >= 0.80 and response <= 14 and hints <= 1 and streak >= 2:
            target = min(3, current + 1)
        elif accuracy < 0.45 or response >= 25 or hints >= 3:
            target = max(1, current - 1)
        else:
            target = current

        rows.append([accuracy, response, hints, current, streak, target])

    return pd.DataFrame(rows, columns=FEATURES + ["target_difficulty"])


def train_decision_tree(save=True):
    df = generate_training_data()
    model = DecisionTreeClassifier(
        max_depth=4,
        min_samples_leaf=8,
        random_state=42,
    )
    model.fit(df[FEATURES], df["target_difficulty"])

    if save:
        MODEL_DIR.mkdir(exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        with MODEL_PATH.open("wb") as f:
            pickle.dump(model, f)
    return model, df


_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    try:
        if MODEL_PATH.exists():
            with MODEL_PATH.open("rb") as f:
                _MODEL = pickle.load(f)
        else:
            _MODEL, _ = train_decision_tree(save=True)
    except Exception:
        _MODEL, _ = train_decision_tree(save=False)
    return _MODEL


def predict_next_difficulty(
    recent_accuracy,
    avg_response_seconds,
    hints_used,
    current_difficulty,
    correct_streak=0,
):
    """Return a difficulty from 1 to 3 and a short human-readable reason."""
    values = [[
        float(recent_accuracy),
        float(avg_response_seconds),
        int(hints_used),
        int(current_difficulty),
        int(correct_streak),
    ]]
    prediction = int(get_model().predict(pd.DataFrame(values, columns=FEATURES))[0])
    prediction = max(1, min(3, prediction))

    if prediction > current_difficulty:
        reason = "Strong recent performance — the next activity is gently increased."
    elif prediction < current_difficulty:
        reason = "The recent pace suggests a gentler activity next."
    else:
        reason = "The next activity stays at a comfortable level."
    return prediction, reason
