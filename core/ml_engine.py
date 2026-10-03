import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def compare_demo_models():
    # Synthetic sample data only; replace with consented, validated data before research use.
    df = pd.DataFrame([
        [1, 0.2, 2, 0], [1, 0.5, 1, 0], [2, 0.8, 0, 1], [2, 0.9, 0, 1],
        [1, 0.4, 3, 0], [2, 0.7, 1, 1], [3, 0.9, 0, 1], [1, 0.3, 2, 0],
        [2, 0.75, 1, 1], [3, 0.95, 0, 1], [1, 0.45, 2, 0], [2, 0.68, 1, 1],
        [3, 0.82, 0, 1], [1, 0.25, 3, 0], [2, 0.73, 0, 1], [3, 0.91, 0, 1],
        [1, 0.38, 2, 0], [2, 0.77, 1, 1], [3, 0.88, 0, 1], [1, 0.48, 2, 0],
    ], columns=["difficulty", "accuracy", "hints", "engagement_group"])
    X = df[["difficulty", "accuracy", "hints"]]
    y = df["engagement_group"]
    # Fit and compare on the sample data; this is a demonstration metric, not validated performance.
    dt = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X, y)
    rf = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42).fit(X, y)
    return {
        "dataset": "synthetic demo data",
        "warning": "Metrics are for code demonstration only and are not clinically validated.",
        "decision_tree_training_accuracy": round(accuracy_score(y, dt.predict(X)), 3),
        "random_forest_training_accuracy": round(accuracy_score(y, rf.predict(X)), 3),
        "features": ["difficulty", "accuracy", "hints_used"],
    }
