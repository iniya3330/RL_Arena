"""Extended Decision Tree controller for RL Arena's level engine.

The model predicts the next difficulty band (1-3) from engagement signals and
reports a confidence score (the tree's class probability). When confidence is
low, the engine keeps the current level instead of guessing.

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
    "overall_skill",
]
MODEL_VERSION = 4
CONFIDENCE_FLOOR = 0.55  # below this the engine keeps the current difficulty
MODEL_DIR = Path(__file__).resolve().parent / "ml_models"
MODEL_PATH = MODEL_DIR / "decision_tree.pkl"
DATA_PATH = MODEL_DIR / "training_data.csv"


def generate_training_data(n=1200, seed=42):
    """Generate transparent synthetic training examples for the demo.

    Sampling is stratified into three player profiles so every difficulty class is
    well represented (plain uniform sampling almost never produces a 'move up' case).
    """
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        current = rng.randint(1, 3)
        profile = rng.random()
        if profile < 0.3:      # strong engagement
            accuracy = round(rng.uniform(0.8, 1.0), 2)
            response = round(rng.uniform(2.5, 14.0), 1)
            hints = rng.randint(0, 1)
            streak = rng.randint(2, 5)
            overall_skill = round(rng.uniform(0.55, 1.0), 2)
        elif profile < 0.6:    # struggling
            accuracy = round(rng.uniform(0.15, 0.45), 2)
            response = round(rng.uniform(12.0, 32.0), 1)
            hints = rng.randint(0, 3)
            streak = rng.randint(0, 1)
            overall_skill = round(rng.uniform(0.0, 0.6), 2)
        else:                  # mixed signals
            accuracy = round(rng.uniform(0.15, 1.0), 2)
            response = round(rng.uniform(2.5, 32.0), 1)
            hints = rng.randint(0, 3)
            streak = rng.randint(0, 5)
            overall_skill = round(rng.uniform(0.0, 1.0), 2)

        # Demonstration policy used to label synthetic examples.
        if accuracy >= 0.80 and response <= 14 and hints <= 1 and streak >= 2 and overall_skill >= 0.55:
            target = min(3, current + 1)
        elif accuracy < 0.45 or response >= 25 or hints >= 3 or (overall_skill < 0.25 and accuracy < 0.6):
            target = max(1, current - 1)
        else:
            target = current

        rows.append([accuracy, response, hints, current, streak, overall_skill, target])

    return pd.DataFrame(rows, columns=FEATURES + ["target_difficulty"])


def train_decision_tree(save=True):
    df = generate_training_data()
    model = DecisionTreeClassifier(max_depth=6, min_samples_leaf=4, random_state=42)
    model.fit(df[FEATURES], df["target_difficulty"])

    if save:
        MODEL_DIR.mkdir(exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        with MODEL_PATH.open("wb") as f:
            pickle.dump({"version": MODEL_VERSION, "features": FEATURES, "model": model}, f)
    return model, df


_MODEL = None


def get_model():
    """Load the saved tree; retrain if it is missing, broken or from an older feature set."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    try:
        if MODEL_PATH.exists():
            with MODEL_PATH.open("rb") as f:
                payload = pickle.load(f)
            if payload.get("version") != MODEL_VERSION or payload.get("features") != FEATURES:
                raise ValueError("stale model")
            _MODEL = payload["model"]
        else:
            _MODEL, _ = train_decision_tree(save=True)
    except Exception:
        _MODEL, _ = train_decision_tree(save=False)
    return _MODEL


def _clamp_difficulty(value):
    return max(1, min(3, int(value)))


def predict_next_difficulty(
    recent_accuracy,
    avg_response_seconds,
    hints_used,
    current_difficulty,
    correct_streak=0,
    overall_skill=0.5,
):
    """Return (difficulty 1-3, human-readable reason, confidence 0-1)."""
    current = _clamp_difficulty(current_difficulty)
    values = pd.DataFrame([[
        float(recent_accuracy),
        float(avg_response_seconds),
        int(hints_used),
        current,
        int(correct_streak),
        float(overall_skill),
    ]], columns=FEATURES)

    model = get_model()
    probabilities = model.predict_proba(values)[0]
    confidence = float(max(probabilities))
    prediction = _clamp_difficulty(model.classes_[probabilities.argmax()])

    if confidence < CONFIDENCE_FLOOR:
        return current, "Signals are mixed, so the same level is kept for now.", round(confidence, 2)

    if prediction > current:
        reason = "Strong recent performance: the next activity is gently increased."
    elif prediction < current:
        reason = "The recent pace suggests a gentler activity next."
    else:
        reason = "The next activity stays at a comfortable level."
    return prediction, reason, round(confidence, 2)


def feature_importances():
    model = get_model()
    return {name: round(float(weight), 3) for name, weight in zip(FEATURES, model.feature_importances_)}
