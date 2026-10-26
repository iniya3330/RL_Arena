"""RL Arena level engine.

One run = ROUND_LIMIT rounds.
  * Calibration (rounds 1-5): five levels from the opening stretch, one per distinct
    domain, chosen per player so two players do not see the same opening.
  * Adaptive (rounds 6-10): the level-selection decision tree (core/level_model.py)
    scores every level the player has unlocked and has not played yet, and picks the one
    whose predicted success is closest to TARGET_SUCCESS. A small seeded tie-break among
    the best few keeps play varied. Domains are not repeated within two rounds when
    there is a choice.

Levels a player has already played are never served again while unplayed ones exist.
Domains are an internal detail: the player-facing payload never includes them.
"""
import random

from django.utils import timezone

from .gamification import overall_skill, skill_map, update_skill
from .level_bank import required_skill, TOTAL_LEVELS
from .level_model import TARGET_SUCCESS, predict_success
from .models import GameQuestion, LevelProgress

CALIBRATION_ROUNDS = 5
ROUND_LIMIT = 10
CALIBRATION_POOL = 40        # opening levels calibration draws from
MIX_WINDOW = 2               # avoid repeating a domain within this many rounds
TOP_K = 3                    # tie-break among the best K candidates


def active_levels():
    return GameQuestion.objects.filter(active=True, level_number__isnull=False)


def unlocked_questions(user):
    skills = skill_map(user)
    return [q for q in active_levels() if skills[q.domain] >= required_skill(q.level_number)]


def locked_count(user):
    return active_levels().count() - len(unlocked_questions(user))


def _played_ids(user):
    return set(LevelProgress.objects.filter(user=user).values_list("question_id", flat=True))


def _recent_signals(answered):
    recent = answered[-5:][::-1]
    if not recent:
        return {"recent_accuracy": 0.6, "avg_response_seconds": 12.0, "hints_used": 0, "correct_streak": 0}
    accuracy = sum(r.is_correct for r in recent) / len(recent)
    avg_response = sum(r.response_seconds for r in recent) / len(recent)
    hints = sum(r.used_hint for r in recent)
    streak = 0
    for r in recent:
        if not r.is_correct:
            break
        streak += 1
    return {"recent_accuracy": accuracy, "avg_response_seconds": avg_response,
            "hints_used": hints, "correct_streak": streak}


def _calibration(user, session, answered, round_number):
    rng = random.Random(user.id * 100003 + session.id)
    played = _played_ids(user) | {a.question_id for a in answered}
    pool = list(GameQuestion.objects.filter(active=True, level_number__lte=CALIBRATION_POOL)
                .exclude(id__in=played))
    used_domains = {a.question.domain for a in answered}
    fresh = [q for q in pool if q.domain not in used_domains] or pool
    question = rng.choice(fresh) if fresh else None
    return {"question": question, "round_number": round_number, "phase": "calibration",
            "predicted": None,
            "reason": f"Calibration round {round_number} of {CALIBRATION_ROUNDS}: we are "
                      "learning how you play before choosing your levels."}


def _candidates(user, answered):
    played = _played_ids(user) | {a.question_id for a in answered}
    unlocked = unlocked_questions(user)
    fresh = [q for q in unlocked if q.id not in played]
    if fresh:
        return fresh, "fresh"
    # Everything unlocked has been played: allow replaying unlocked levels not yet cleared.
    cleared = set(LevelProgress.objects.filter(user=user, cleared=True).values_list("question_id", flat=True))
    retry = [q for q in unlocked if q.id not in cleared and q.id not in {a.question_id for a in answered}]
    if retry:
        return retry, "retry"
    return [], "none"


def _adaptive(user, session, answered, round_number):
    candidates, source = _candidates(user, answered)
    if not candidates:
        return {"question": None, "round_number": round_number, "phase": "adaptive",
                "predicted": None, "reason": "You have cleared every level unlocked for you. Keep training to open more."}

    skills = skill_map(user)
    overall = overall_skill(user) * 100
    signals = _recent_signals(answered)
    rows = [{
        "domain_skill": skills[q.domain],
        "level_position": (q.level_number - 1) / (TOTAL_LEVELS - 1),
        "difficulty": q.difficulty,
        **signals,
        "overall_skill": overall,
    } for q in candidates]
    probabilities = predict_success(rows)

    recent_domains = {a.question.domain for a in answered[-MIX_WINDOW:]}
    scored = sorted(zip(candidates, probabilities), key=lambda qp: abs(qp[1] - TARGET_SUCCESS))
    preferred = [qp for qp in scored if qp[0].domain not in recent_domains] or scored
    best = preferred[:TOP_K]
    rng = random.Random(f"{user.id}-{session.id}-{round_number}")
    question, probability = rng.choice(best)

    reason = (f"The engine chose level {question.level_number} because it predicts about "
              f"{round(probability * 100)}% success, close to the {round(TARGET_SUCCESS * 100)}% target.")
    if source == "retry":
        reason += " You have played all your fresh levels, so this one is a retry."
    return {"question": question, "round_number": round_number, "phase": "adaptive",
            "predicted": round(probability, 3), "reason": reason}


def choose_next_question(user, session):
    """Returns a dict: question, round_number, phase, predicted, reason."""
    answered = list(session.responses.select_related("question").order_by("id"))
    round_number = len(answered) + 1
    if round_number <= CALIBRATION_ROUNDS:
        return _calibration(user, session, answered, round_number)
    return _adaptive(user, session, answered, round_number)


def record_outcome(user, question, correct, used_hint):
    progress, _ = LevelProgress.objects.get_or_create(user=user, question=question)
    progress.attempts += 1
    cleared_now = False
    if correct and not used_hint and not progress.cleared:
        progress.cleared = True
        progress.cleared_at = timezone.now()
        cleared_now = True
    progress.save()
    new_skill = update_skill(user, question.domain, correct, question.difficulty, used_hint)
    return {"cleared_now": cleared_now, "skill": new_skill}
