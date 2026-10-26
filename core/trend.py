"""Game-performance trend: a player's first three runs compared with their latest three.

This describes change in game accuracy over time. It is NOT a medical, dementia or
diagnostic assessment, and should be read together with a clinician's judgement.
"""
MIN_RUNS = 6
CHANGE_THRESHOLD = 5.0   # percentage points


def trend_summary(accuracies):
    values = [float(a) for a in accuracies]
    n = len(values)
    if n < MIN_RUNS:
        return {"status": "insufficient", "label": f"Needs {MIN_RUNS - n} more runs",
                "before": None, "now": None, "change": None, "runs": n}
    before = round(sum(values[:3]) / 3, 1)
    now = round(sum(values[-3:]) / 3, 1)
    change = round(now - before, 1)
    if change >= CHANGE_THRESHOLD:
        status, label = "improving", "Improving"
    elif change <= -CHANGE_THRESHOLD:
        status, label = "lower", "Lower than before"
    else:
        status, label = "steady", "Steady"
    return {"status": status, "label": label, "before": before, "now": now, "change": change, "runs": n}
