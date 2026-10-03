from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import GameSession, Reminder


def home(request):
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("caregiver" if request.user.is_staff else "dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "patient")

        user = User.objects.filter(email__iexact=email).first()
        if user:
            user = authenticate(request, username=user.username, password=password)

        if user is not None:
            if role == "caregiver" and not user.is_staff:
                messages.error(request, "This demo account is not a caregiver account.")
            elif role == "patient" and user.is_staff:
                messages.error(request, "Choose the caregiver role for this account.")
            else:
                login(request, user)
                return redirect("caregiver" if role == "caregiver" else "dashboard")
        else:
            messages.error(request, "Email or password is incorrect. Use one of the demo accounts shown below.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    sessions = GameSession.objects.filter(
        patient=request.user, completed=True
    ).order_by("-started_at")[:20]
    reminders = Reminder.objects.filter(
        patient=request.user, active=True
    ).order_by("reminder_time", "-created_at")
    return render(request, "dashboard.html", {
        "sessions": sessions,
        "reminders": reminders,
    })


@login_required
def caregiver_dashboard(request):
    if not request.user.is_staff:
        return redirect("dashboard")
    patients = User.objects.filter(is_staff=False).prefetch_related("game_sessions")
    return render(request, "caregiver.html", {"patients": patients})
