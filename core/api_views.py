import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import GameQuestion, GameSession, GameResponse, Reminder
from .serializers import GameQuestionSerializer, ReminderSerializer
from .adaptive import choose_next_question
from .ml_engine import compare_demo_models

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def questions(request):
    qs = GameQuestion.objects.filter(active=True).order_by("domain", "difficulty")
    return Response(GameQuestionSerializer(qs, many=True).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_session(request):
    session = GameSession.objects.create(patient=request.user)
    question = GameQuestion.objects.filter(active=True).order_by("?").first()
    return Response({"session_id": session.id, "question": GameQuestionSerializer(question).data if question else None})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def answer_question(request):
    session_id = request.data.get("session_id")
    question_id = request.data.get("question_id")
    answer = str(request.data.get("answer", ""))[:200]
    used_hint = bool(request.data.get("used_hint", False))
    response_seconds = max(0.0, min(float(request.data.get("response_seconds", 0)), 3600.0))
    try:
        session = GameSession.objects.get(id=session_id, patient=request.user, completed=False)
        question = GameQuestion.objects.get(id=question_id, active=True)
    except (GameSession.DoesNotExist, GameQuestion.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Session or question not found."}, status=400)
    correct = answer.strip().casefold() == question.correct_answer.strip().casefold()
    GameResponse.objects.create(session=session, question=question, answer=answer, is_correct=correct,
                                response_seconds=response_seconds, used_hint=used_hint)
    session.total_questions += 1
    session.correct_answers += int(correct)
    session.hints_used += int(used_hint)
    count = session.responses.count()
    session.average_response_seconds = sum(r.response_seconds for r in session.responses.all()) / max(count, 1)
    session.save()
    next_question, next_difficulty, adaptation_reason = choose_next_question(
        request.user, question, correct
    )
    return Response({
        "correct": correct,
        "feedback": "Well done! Let's try another." if correct else "Good try. Let's practise together.",
        "score_percent": session.score_percent,
        "next_question": GameQuestionSerializer(next_question).data if next_question else None,
        "next_difficulty": next_difficulty,
        "adaptation_reason": adaptation_reason,
        "session_id": session.id,
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_session(request):
    session_id = request.data.get("session_id")
    try:
        session = GameSession.objects.get(id=session_id, patient=request.user, completed=False)
    except (GameSession.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Session not found."}, status=400)
    session.completed = True
    session.ended_at = timezone.now()
    session.save()
    return Response({"message": "Session saved", "score_percent": session.score_percent, "total_questions": session.total_questions})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics(request):
    sessions = GameSession.objects.filter(patient=request.user).order_by("started_at")
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

@login_required
def report_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from io import BytesIO
    sessions = GameSession.objects.filter(patient=request.user).order_by("-started_at")[:20]
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 55
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "CogniCare NER - Cognitive Game Summary")
    y -= 30
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Demo account: {request.user.username}")
    y -= 18
    pdf.drawString(50, y, "Scores indicate game engagement only, not clinical diagnosis.")
    y -= 30
    for s in sessions:
        line = f"{s.started_at.strftime('%d-%m-%Y %H:%M')} | score {s.score_percent}% | questions {s.total_questions} | hints {s.hints_used}"
        pdf.drawString(50, y, line[:110])
        y -= 18
        if y < 60:
            pdf.showPage()
            y = height - 55
            pdf.setFont("Helvetica", 10)
    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cognicare-report.pdf"'
    return response
