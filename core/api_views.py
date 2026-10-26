from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (GameQuestion, GameSession, GameResponse, Reminder, Badge,
                     PlayerBadge, LeaderboardEntry, LevelProgress)
from .serializers import GameQuestionSerializer, ReminderSerializer
from .adaptive import (choose_next_question, record_outcome, unlocked_questions, active_levels,
                       locked_count, ROUND_LIMIT, CALIBRATION_ROUNDS)
from .decision_tree import predict_next_difficulty, feature_importances, CONFIDENCE_FLOOR
from .gamification import (add_xp, ensure_player_xp, evaluate_badges, level_for_xp, level_progress,
                           overall_skill, player_stats, refresh_leaderboard, domain_scores, rank_change,
                           xp_for_response, RADAR_DOMAINS, RADAR_LABELS,
                           SESSION_COMPLETE_XP, PERFECT_SESSION_XP)
from .level_bank import TOTAL_LEVELS, required_skill
from .ml_engine import compare_demo_models

BASE_XP = 10


# ---------- helpers ----------

def _question_payload(question):
    """Player-facing question. Domains are internal, so they are not sent."""
    if question is None:
        return None
    return {**GameQuestionSerializer(question).data, "level_number": question.level_number}


def _current_streak(session):
    streak = 0
    for is_correct in session.responses.order_by("-id").values_list("is_correct", flat=True):
        if not is_correct:
            break
        streak += 1
    return streak


def _badge_payload(badge):
    return {"code": badge.code, "name": badge.name, "icon": badge.icon,
            "description": badge.description, "glow": badge.glow}


def _clamped(params, name, default, lo, hi, cast=float):
    try:
        value = cast(params.get(name, default))
    except (TypeError, ValueError):
        value = cast(default)
    return max(lo, min(hi, value))


def _overall_payload(user):
    """Single overall skill for the player. Per-domain skill stays in the admin panel."""
    score = round(overall_skill(user) * 100, 1)
    return {"score": score, "unlocks_up_to_level": min(TOTAL_LEVELS, int(score * TOTAL_LEVELS / 100) + 1)}


# ---------- game endpoints ----------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def questions(request):
    qs = active_levels().order_by("level_number")
    return Response(GameQuestionSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_session(request):
    session = GameSession.objects.create(patient=request.user)
    choice = choose_next_question(request.user, session)
    return Response({
        "session_id": session.id,
        "round": {"number": choice["round_number"], "total": ROUND_LIMIT, "phase": choice["phase"]},
        "question": _question_payload(choice["question"]),
        "reason": choice["reason"],
        "predicted_success": choice["predicted"],
        "level": level_progress(ensure_player_xp(request.user).total_xp),
        "skill": _overall_payload(request.user),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def answer_question(request):
    session_id = request.data.get("session_id")
    question_id = request.data.get("question_id")
    answer = str(request.data.get("answer", ""))[:200]
    used_hint = bool(request.data.get("used_hint", False))
    try:
        response_seconds = max(0.0, min(float(request.data.get("response_seconds", 0)), 3600.0))
        session = GameSession.objects.get(id=session_id, patient=request.user, completed=False)
        question = GameQuestion.objects.get(id=question_id, active=True)
    except (GameSession.DoesNotExist, GameQuestion.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Session or question not found."}, status=400)

    correct = answer.strip().casefold() == question.correct_answer.strip().casefold()
    GameResponse.objects.create(session=session, question=question, answer=answer, is_correct=correct,
                                response_seconds=response_seconds, used_hint=used_hint)
    outcome = record_outcome(request.user, question, correct, used_hint)

    xp_gained = xp_for_response(BASE_XP, question.difficulty, correct)
    session.total_questions += 1
    session.correct_answers += int(correct)
    session.hints_used += int(used_hint)
    streak = _current_streak(session)
    session.best_streak = max(session.best_streak, streak)
    session.xp_earned += xp_gained
    responses = list(session.responses.all())
    session.average_response_seconds = sum(r.response_seconds for r in responses) / max(len(responses), 1)
    session.save()
    total_xp = add_xp(request.user, xp_gained)

    round_complete = session.total_questions >= ROUND_LIMIT
    payload = {
        "correct": correct,
        "correct_answer": question.correct_answer,
        "feedback": "Well done! Let's try another." if correct else "Good try. Let's practise together.",
        "score_percent": session.score_percent,
        "xp_gained": xp_gained,
        "total_xp": total_xp,
        "streak": streak,
        "best_streak": session.best_streak,
        "cleared_now": outcome["cleared_now"],
        "skill": outcome["skill"],
        "round_complete": round_complete,
        "session_id": session.id,
    }
    if not round_complete:
        choice = choose_next_question(request.user, session)
        payload.update({
            "next_question": _question_payload(choice["question"]),
            "round": {"number": choice["round_number"], "total": ROUND_LIMIT, "phase": choice["phase"]},
            "predicted_success": choice["predicted"],
            "adaptation_reason": choice["reason"],
        })
    return Response(payload)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_session(request):
    session_id = request.data.get("session_id")
    try:
        session = GameSession.objects.get(id=session_id, patient=request.user, completed=False)
    except (GameSession.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Session not found."}, status=400)

    level_before = level_for_xp(ensure_player_xp(request.user).total_xp)
    perfect = session.total_questions >= 5 and session.correct_answers == session.total_questions
    bonus = SESSION_COMPLETE_XP + (PERFECT_SESSION_XP if perfect else 0)
    session.completed = True
    session.ended_at = timezone.now()
    session.xp_earned += bonus
    session.save()
    add_xp(request.user, bonus)

    new_badges = evaluate_badges(request.user)
    total_xp = ensure_player_xp(request.user).total_xp
    refresh_leaderboard()
    progress = level_progress(total_xp)
    return Response({
        "message": "Session saved",
        "score_percent": session.score_percent,
        "total_questions": session.total_questions,
        "xp_gained": session.xp_earned,
        "total_xp": total_xp,
        "level": progress["level"],
        "level_up": progress["level"] > level_before,
        "perfect": perfect,
        "new_badges": [_badge_payload(b) for b in new_badges],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics(request):
    sessions = GameSession.objects.filter(patient=request.user, completed=True).order_by("started_at")
    data = [{
        "date": s.started_at.strftime("%d %b"),
        "score": s.score_percent,
        "questions": s.total_questions,
        "hints": s.hints_used,
    } for s in sessions]
    avg = round(sum(s["score"] for s in data) / len(data)) if data else 0
    return Response({"sessions": data, "average_score": avg, "total_sessions": len(data),
                     "total_questions": sum(s["questions"] for s in data)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ml_compare(request):
    return Response(compare_demo_models())


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def reminders(request):
    if request.method == "GET":
        qs = Reminder.objects.filter(patient=request.user, active=True).order_by("reminder_time")
        return Response(ReminderSerializer(qs, many=True).data)
    serializer = ReminderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(patient=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ---------- RL Arena endpoints ----------

BATCH_SIZE = 10


def _batch_view(user, unlocked, progress):
    """Only the current batch of ten is shown, plus a one-line preview of the next batch."""
    unlocked_numbers = {q.level_number for q in unlocked}
    highest = max(unlocked_numbers, default=1)
    start = ((highest - 1) // BATCH_SIZE) * BATCH_SIZE + 1
    end = min(TOTAL_LEVELS, start + BATCH_SIZE - 1)
    by_number = {q.level_number: q.id for q in active_levels()}
    levels = []
    for number in range(start, end + 1):
        qid = by_number.get(number)
        state = "locked"
        if number in unlocked_numbers:
            state = "cleared" if qid in progress and progress[qid].cleared else "open"
        levels.append({"level_number": number, "state": state})
    batch = {
        "number": (start - 1) // BATCH_SIZE + 1,
        "start": start, "end": end, "size": BATCH_SIZE,
        "cleared": sum(1 for lv in levels if lv["state"] == "cleared"),
        "levels": levels,
        "next": None,
    }
    if end < TOTAL_LEVELS:
        next_start = end + 1
        next_end = min(TOTAL_LEVELS, next_start + BATCH_SIZE - 1)
        batch["next"] = {
            "number": (next_start - 1) // BATCH_SIZE + 1,
            "start": next_start, "end": next_end,
            "required_skill": required_skill(next_start),
            "current_skill": round(overall_skill(user) * 100, 1),
        }
    return batch


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def arena_levels(request):
    """Levels this player has unlocked, with cleared state, and the next unlock. No domains."""
    unlocked = unlocked_questions(request.user)
    progress = {p.question_id: p for p in LevelProgress.objects.filter(user=request.user)}
    overall = round(overall_skill(request.user) * 100, 1)
    levels = [{
        "level_number": q.level_number,
        "cleared": bool(progress.get(q.id) and progress[q.id].cleared),
        "attempts": progress[q.id].attempts if q.id in progress else 0,
    } for q in sorted(unlocked, key=lambda q: q.level_number)]

    unlocked_ids = {q.id for q in unlocked}
    next_unlock = None
    for q in active_levels().order_by("level_number"):
        if q.id in unlocked_ids:
            continue
        need = required_skill(q.level_number)
        next_unlock = {"level_number": q.level_number, "required_skill": need,
                       "current_skill": overall, "gap": round(max(0, need - overall), 1)}
        break

    return Response({
        "total_levels": TOTAL_LEVELS,
        "batch": _batch_view(request.user, unlocked, progress),
        "unlocked_count": len(levels),
        "cleared_count": sum(1 for lv in levels if lv["cleared"]),
        "locked_count": locked_count(request.user),
        "levels": levels,
        "next_unlock": next_unlock,
        "calibration_rounds": CALIBRATION_ROUNDS,
        "round_limit": ROUND_LIMIT,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def player_progress(request):
    """2. XP, level ring, skills, badge wall (earned glow, locked fog) and raw stats."""
    total_xp = ensure_player_xp(request.user).total_xp
    stats = player_stats(request.user)
    earned = {pb.badge_id: pb.earned_at for pb in PlayerBadge.objects.filter(user=request.user)}
    badges = []
    for badge in Badge.objects.all():
        current = stats.get(badge.criteria_type, 0)
        badges.append({
            "code": badge.code, "name": badge.name, "icon": badge.icon,
            "description": badge.description, "glow": badge.glow,
            "earned": badge.id in earned,
            "earned_at": earned[badge.id].strftime("%d %b %Y") if badge.id in earned else None,
            "progress": min(current, badge.threshold), "threshold": badge.threshold,
        })
    return Response({
        "level": level_progress(total_xp),
        "skill": _overall_payload(request.user),
        "badges": badges,
        "earned_count": len(earned),
        "total_badges": len(badges),
        "stats": stats,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """3. Animated leaderboard data with rank-change arrows."""
    if not LeaderboardEntry.objects.exists():
        refresh_leaderboard()
    entries = LeaderboardEntry.objects.select_related("user").order_by("rank")[:20]
    rows = [{
        "rank": e.rank,
        "previous_rank": e.previous_rank,
        "change": rank_change(e.previous_rank, e.rank),
        "name": e.user.first_name or e.user.username,
        "total_xp": e.total_xp,
        "level": level_for_xp(e.total_xp),
        "sessions": e.sessions_completed,
        "accuracy_percent": e.accuracy_percent,
        "is_me": e.user_id == request.user.id,
    } for e in entries]
    return Response({"entries": rows, "my_rank": next((r["rank"] for r in rows if r["is_me"]), None)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cognitive_report(request):
    """4. Radar chart data across the six domains: recent answers vs. all-time."""
    recent = domain_scores(request.user, window=15)
    overall = domain_scores(request.user)
    answers = {d: GameResponse.objects.filter(session__patient=request.user, question__domain=d).count()
               for d in RADAR_DOMAINS}
    return Response({
        "domains": RADAR_DOMAINS,
        "labels": RADAR_LABELS,
        "recent": [recent[d] for d in RADAR_DOMAINS],
        "overall": [overall[d] for d in RADAR_DOMAINS],
        "answers": [answers[d] for d in RADAR_DOMAINS],
        "disclaimer": "Engagement scores from game play only. Not a clinical assessment.",
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ml_predict(request):
    """5. Preview the Extended Decision Tree: next band, confidence and feature weights."""
    params = request.query_params
    inputs = {
        "accuracy": _clamped(params, "accuracy", 0.6, 0.0, 1.0),
        "seconds": _clamped(params, "seconds", 12.0, 0.0, 3600.0),
        "hints": _clamped(params, "hints", 0, 0, 5, int),
        "difficulty": _clamped(params, "difficulty", 1, 1, 3, int),
        "streak": _clamped(params, "streak", 0, 0, 20, int),
        "overall_skill": _clamped(params, "overall_skill", 0.5, 0.0, 1.0),
    }
    prediction, reason, confidence = predict_next_difficulty(
        inputs["accuracy"], inputs["seconds"], inputs["hints"], inputs["difficulty"],
        inputs["streak"], inputs["overall_skill"],
    )
    return Response({
        "input": inputs,
        "next_band": prediction,
        "confidence": confidence,
        "confidence_floor": CONFIDENCE_FLOOR,
        "held_at_current_level": confidence < CONFIDENCE_FLOOR,
        "reason": reason,
        "feature_importances": feature_importances(),
        "model": "Extended Decision Tree (synthetic demo data, not clinically validated)",
    })


@login_required
def report_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from io import BytesIO
    sessions = GameSession.objects.filter(patient=request.user).order_by("-started_at")[:20]
    progress = level_progress(ensure_player_xp(request.user).total_xp)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 55
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "RL Arena - Cognitive Game Summary")
    y -= 30
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Player: {request.user.first_name or request.user.username}   Level {progress['level']}   XP {progress['total_xp']}")
    y -= 18
    pdf.drawString(50, y, "Scores indicate game engagement only, not clinical diagnosis.")
    y -= 30
    for s in sessions:
        line = (f"{s.started_at.strftime('%d-%m-%Y %H:%M')} | score {s.score_percent}% | "
                f"questions {s.total_questions} | hints {s.hints_used} | best streak {s.best_streak}")
        pdf.drawString(50, y, line[:118])
        y -= 18
        if y < 60:
            pdf.showPage()
            y = height - 55
            pdf.setFont("Helvetica", 10)
    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="rl-arena-report.pdf"'
    return response
