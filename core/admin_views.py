"""Admin (caregiver) panel: player list with accuracy, detail pages, status toggle, CSV export and JSON."""
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .accounts import accuracy_band
from .gamification import (domain_scores, ensure_player_xp, level_progress, refresh_leaderboard,
                           skill_map)
from .level_bank import DOMAIN_LABELS, DOMAINS
from .models import GameResponse, GameSession, LevelProgress, PlayerBadge, LeaderboardEntry, Reminder
from .trend import trend_summary


def player_rows():
    rows = []
    for user in User.objects.filter(is_staff=False).order_by("first_name", "username"):
        answers = GameResponse.objects.filter(session__patient=user)
        total = answers.count()
        correct = answers.filter(is_correct=True).count()
        accuracy = round(100 * correct / total) if total else None
        sessions = GameSession.objects.filter(patient=user)
        last = sessions.order_by("-started_at").first()
        xp = ensure_player_xp(user).total_xp
        rows.append({
            "id": user.id,
            "name": user.first_name or user.username,
            "email": user.email,
            "active": user.is_active,
            "joined": user.date_joined.strftime("%d %b %Y"),
            "runs": sessions.filter(completed=True).count(),
            "answers": total,
            "correct": correct,
            "accuracy": accuracy,
            "band": accuracy_band(accuracy),
            "level": level_progress(xp)["level"],
            "xp": xp,
            "cleared": LevelProgress.objects.filter(user=user, cleared=True).count(),
            "badges": PlayerBadge.objects.filter(user=user).count(),
            "last_active": last.started_at.strftime("%d %b %Y, %H:%M") if last else "Never",
        })
    return rows


def _summary(rows):
    scored = [r["accuracy"] for r in rows if r["accuracy"] is not None]
    return {
        "players": len(rows),
        "active": sum(1 for r in rows if r["active"]),
        "answers": sum(r["answers"] for r in rows),
        "average_accuracy": round(sum(scored) / len(scored)) if scored else 0,
        "bands": {b: sum(1 for r in rows if r["band"] == b) for b in ("high", "mid", "low", "none")},
    }


def _admin_only(request):
    return request.user.is_staff


@login_required
def admin_panel(request):
    if not _admin_only(request):
        return redirect("dashboard")
    rows = player_rows()
    if not LeaderboardEntry.objects.exists():
        refresh_leaderboard()
    board = LeaderboardEntry.objects.select_related("user").order_by("rank")[:10]
    return render(request, "admin_panel.html", {"players": rows, "summary": _summary(rows), "board": board})


def level_history(player):
    """Every level this player was given, with attempts and results. Levels are numbered 1-500."""
    answers = (GameResponse.objects.filter(session__patient=player, question__level_number__isnull=False)
               .select_related("question").order_by("created_at"))
    by_level = {}
    for answer in answers:
        number = answer.question.level_number
        entry = by_level.setdefault(number, {
            "level": number, "batch": (number - 1) // 10 + 1, "attempts": 0, "correct": 0,
            "first": answer.created_at, "last": answer.created_at, "last_result": "",
        })
        entry["attempts"] += 1
        entry["correct"] += int(answer.is_correct)
        entry["last"] = answer.created_at
        entry["last_result"] = "Correct" if answer.is_correct else "Missed"
    rows = []
    for entry in sorted(by_level.values(), key=lambda e: e["level"]):
        rows.append({
            **entry,
            "first": entry["first"].strftime("%d %b %Y"),
            "last": entry["last"].strftime("%d %b %Y, %H:%M"),
            "score": round(100 * entry["correct"] / entry["attempts"]),
        })
    return rows


@login_required
def admin_user_detail(request, user_id):
    if not _admin_only(request):
        return redirect("dashboard")
    player = get_object_or_404(User, id=user_id, is_staff=False)
    row = next(r for r in player_rows() if r["id"] == player.id)
    skills = skill_map(player)
    accuracy = domain_scores(player)
    completed = list(GameSession.objects.filter(patient=player, completed=True).order_by("started_at"))
    sessions = GameSession.objects.filter(patient=player).order_by("-started_at")[:25]
    trend = trend_summary([s.score_percent for s in completed])
    levels = level_history(player)
    return render(request, "admin_user.html", {
        "p": row,
        "domains": [{"label": DOMAIN_LABELS[d], "skill": round(skills[d]), "accuracy": accuracy[d]} for d in DOMAINS],
        "sessions": sessions,
        "reminders": Reminder.objects.filter(patient=player, active=True),
        "trend": trend,
        "run_chart": {"labels": [s.started_at.strftime("%d %b") for s in completed],
                      "scores": [s.score_percent for s in completed]},
        "levels": levels,
        "levels_reached": len(levels),
        "highest_level": levels[-1]["level"] if levels else None,
    })


@login_required
@require_POST
def toggle_user(request, user_id):
    if not _admin_only(request):
        return redirect("dashboard")
    player = get_object_or_404(User, id=user_id, is_staff=False)
    player.is_active = not player.is_active
    player.save(update_fields=["is_active"])
    state = "re-enabled" if player.is_active else "disabled"
    messages.success(request, f"{player.first_name or player.username} has been {state}.")
    return redirect(request.POST.get("next") or "admin_panel")


@login_required
def export_csv(request):
    if not _admin_only(request):
        return redirect("dashboard")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="rl-arena-players.csv"'
    writer = csv.writer(response)
    writer.writerow(["Name", "Email", "Status", "Joined", "Runs", "Answers", "Correct", "Accuracy %",
                     "Level", "XP", "Levels cleared", "Badges", "Last active"])
    for r in player_rows():
        writer.writerow([r["name"], r["email"], "active" if r["active"] else "disabled", r["joined"],
                         r["runs"], r["answers"], r["correct"], r["accuracy"] if r["accuracy"] is not None else "",
                         r["level"], r["xp"], r["cleared"], r["badges"], r["last_active"]])
    return response


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_players_api(request):
    rows = player_rows()
    return Response({"players": rows, "summary": _summary(rows)})
