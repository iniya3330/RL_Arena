from .models import GameQuestion
from .decision_tree import predict_next_difficulty

def choose_next_question(patient, previous_question=None, was_correct=None):
    """ML-guided adaptive selection. This is engagement adaptation, not diagnosis."""
    recent_responses = []
    try:
        latest_session = patient.game_sessions.order_by("-started_at").first()
        if latest_session:
            recent_responses = list(
                latest_session.responses.order_by("-created_at")[:5]
            )
    except AttributeError:
        pass

    if recent_responses:
        accuracy = sum(r.is_correct for r in recent_responses) / len(recent_responses)
        avg_response = sum(r.response_seconds for r in recent_responses) / len(recent_responses)
        hints = sum(r.used_hint for r in recent_responses)
        streak = 0
        for response in recent_responses:
            if response.is_correct:
                streak += 1
            else:
                break
    else:
        accuracy, avg_response, hints, streak = 0.60, 12.0, 0, 0

    current = previous_question.difficulty if previous_question else 1
    target, reason = predict_next_difficulty(
        accuracy, avg_response, hints, current, streak
    )

    qs = GameQuestion.objects.filter(active=True, difficulty=target)
    if previous_question:
        qs = qs.exclude(id=previous_question.id)

    question = qs.order_by("?").first()
    if question is None:
        question = (
            GameQuestion.objects.filter(active=True)
            .exclude(id=getattr(previous_question, "id", None))
            .order_by("?").first()
        )
    return question, target, reason
