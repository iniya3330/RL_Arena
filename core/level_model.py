"""Level-selection decision tree.

A scikit-learn DecisionTreeClassifier learns the probability that a player answers a
given level correctly. For every unlocked, not-yet-played level the engine asks the tree
for that probability and picks the level whose predicted success is closest to TARGET.
That keeps each round challenging without being trivial or frustrating.

Trained on synthetic demonstration data (seeded, so it is reproducible). It is not
clinically validated and does not diagnose anything.
"""
import math
import random
import threading

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

FEATURES = [
    "domain_skill",        # 0-100, skill in the candidate level's domain
    "level_position",      # 0-1, how far along the 500 levels this level is
    "difficulty",          # 1-3
    "recent_accuracy",     # 0-1, last five answers
    "correct_streak",      # 0-5
    "hints_used",          # 0-5, last five answers
    "avg_response_seconds",
    "overall_skill",       # 0-100 average across domains
]
TARGET_SUCCESS = 0.75     # the engine aims for a level the player is ~75% likely to clear
TRAIN_SAMPLES = 3000
RANDOM_SEED = 42

_lock = threading.Lock()
_model = None


def _sigmoid(x):
    return 1 / (1 + math.exp(-x))


def generate_training_data(n=TRAIN_SAMPLES, seed=RANDOM_SEED):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        domain_skill = rng.uniform(0, 100)
        position = rng.uniform(0, 1)
        difficulty = rng.randint(1, 3)
        accuracy = rng.uniform(0, 1)
        streak = rng.randint(0, 5)
        hints = rng.randint(0, 5)
        response = rng.uniform(2, 30)
        overall = rng.uniform(0, 100)
        # Demonstration ground truth: skill has to meet the level's requirement,
        # recent accuracy and streak help, hints and slow answers hurt.
        logit = (0.06 * (domain_skill - position * 100)
                 + 1.5 * (accuracy - 0.6)
                 + 0.12 * min(streak, 5)
                 - 0.25 * hints
                 - 0.03 * max(0.0, response - 10)
                 + 0.02 * (overall - 50)
                 - 0.3 * (difficulty - 1))
        label = 1 if rng.random() < _sigmoid(logit) else 0
        rows.append([domain_skill, position, difficulty, accuracy, streak, hints, response, overall, label])
    return pd.DataFrame(rows, columns=FEATURES + ["success"])


def get_model():
    global _model
    with _lock:
        if _model is None:
            df = generate_training_data()
            _model = DecisionTreeClassifier(max_depth=6, min_samples_leaf=8, random_state=RANDOM_SEED)
            _model.fit(df[FEATURES], df["success"])
    return _model


def predict_success(rows):
    """rows: list of feature dicts (keys = FEATURES). Returns a list of probabilities."""
    if not rows:
        return []
    frame = pd.DataFrame([[float(r[f]) for f in FEATURES] for r in rows], columns=FEATURES)
    model = get_model()
    classes = list(model.classes_)
    if 1 not in classes:
        return [0.0] * len(rows)
    column = classes.index(1)
    return [float(p) for p in model.predict_proba(frame)[:, column]]


def feature_importances():
    model = get_model()
    return {name: round(float(w), 3) for name, w in zip(FEATURES, model.feature_importances_)}
