from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .accounts import home_for, login_problem, validate_signup, role_for_email
from .gamification import ensure_player_xp, level_progress
from .i18n import LANGUAGES
from .models import GameSession, Reminder


def home(request):
    return render(request, "home.html")


def set_language(request, code):
    """Store the chosen interface language in the session, then return to the same page."""
    if code in LANGUAGES:
        request.session["lang"] = code
    target = request.META.get("HTTP_REFERER", "/")
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                           require_https=request.is_secure()):
        target = "/"
    return redirect(target)


def _safe_next(request):
    """The page to return to after signing in (e.g. an admin's player page), or None.
    Only same-site paths are accepted, so this cannot send people to another website."""
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                                  require_https=request.is_secure()):
        return target
    return None


def login_view(request):
    next_url = _safe_next(request)
    if request.user.is_authenticated:
        return redirect(next_url or home_for(request.user.is_staff))
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        candidate = User.objects.filter(email__iexact=email).first()
        account = authenticate(request, username=candidate.username, password=password) if candidate else None
        if account is None:
            messages.error(request, "Email or password is incorrect.")
        elif (problem := login_problem(email, account.is_staff, account.is_active)):
            messages.error(request, problem)
        else:
            login(request, account)
            return redirect(next_url or home_for(account.is_staff))
    return render(request, "login.html")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect(home_for(request.user.is_staff))
    values = {"name": "", "email": ""}
    if request.method == "POST":
        name = request.POST.get("name", "").strip()[:150]
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm", "")
        values = {"name": name, "email": email}
        exists = User.objects.filter(email__iexact=email).exists()
        errors = validate_signup(name, email, password, confirm, exists)
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=name, is_staff=(role_for_email(email) == "admin"),
            )
            login(request, user)
            return redirect(home_for(user.is_staff))
    return render(request, "signup.html", {"values": values})


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("admin_panel")
    sessions = GameSession.objects.filter(patient=request.user, completed=True).order_by("-started_at")[:20]
    reminders = Reminder.objects.filter(patient=request.user, active=True).order_by("reminder_time", "-created_at")
    xp = ensure_player_xp(request.user).total_xp
    return render(request, "dashboard.html", {
        "sessions": sessions,
        "reminders": reminders,
        "level": level_progress(xp),
        "reminder_data": [{"id": r.id, "title": r.title, "type": r.reminder_type, "notes": r.notes,
                           "time": r.reminder_time.strftime("%H:%M") if r.reminder_time else ""}
                          for r in reminders],
    })