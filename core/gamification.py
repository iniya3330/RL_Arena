
from django.contrib.auth.models import User
from django.db.models import F, Sum

from .level_bank import DOMAINS, DOMAIN_LABELS

XP_PER_LEVEL = 150
DIFFICULTY_XP_MULTIPLIER = {1: 1.0, 2: 1.5, 3: 2.0}
WRONG_ANSWER_XP = 2          # effort is still rewarded a little
SESSION_COMPLETE_XP = 25
PERFECT_SESSION_XP = 40
RADAR_DOMAINS = DOMAINS
RADAR_LABELS = [DOMAIN_LABELS[d] for d in DOMAINS]
INITIAL_SKILL = 30.0         # every domain starts here, so early levels are open to everyone
SKILL_RATE = 0.12            # how quickly a single answer moves a domain's skill
SKILL_WEIGHT = {1: 0.8, 2: 1.0, 3: 1.2}

# (code, name, description, icon, criteria_type, threshold, glow colour)
BADGE_CATALOG = [
    ("first-steps", "First Steps", "Complete your first session", "🌱", "sessions", 1, "#5ef2b0"),
    ("regular-racer", "Regular Racer", "Complete 5 sessions", "🏁", "sessions", 5, "#5ef2b0"),
    ("arena-veteran", "Arena Veteran", "Complete 10 sessions", "🏟️", "sessions", 10, "#5ef2b0"),
    ("iron-routine", "Iron Routine", "Complete 25 sessions", "⚙️", "sessions", 25, "#5ef2b0"),
    ("sharp-start", "Sharp Start", "Answer 10 questions correctly", "🎯", "correct", 10, "#5ec8ff"),
    ("quick-mind", "Quick Mind", "Answer 50 questions correctly", "⚡", "correct", 50, "#5ec8ff"),
    ("century-club", "Century Club", "Answer 100 questions correctly", "💯", "correct", 100, "#5ec8ff"),
    ("hot-streak", "Hot Streak", "Get 3 correct in a row", "🔥", "streak", 3, "#ff9f5e"),
    ("on-fire", "On Fire", "Get 5 correct in a row", "☄️", "streak", 5, "#ff9f5e"),
    ("unstoppable", "Unstoppable", "Get 8 correct in a row", "🌋", "streak", 8, "#ff9f5e"),
    ("rising-star", "Rising Star", "Reach level 2", "⭐", "level", 2, "#ffe05e"),
    ("orbit-runner", "Orbit Runner", "Reach level 5", "🪐", "level", 5, "#ffe05e"),
    ("galaxy-guide", "Galaxy Guide", "Reach level 10", "🌌", "level", 10, "#ffe05e"),
    ("flawless-round", "Flawless Round", "Score 100% in a 5+ question session", "💎", "perfect", 1, "#c792ff"),
    ("perfectionist", "Perfectionist", "Score 100% in 3 sessions", "👑", "perfect", 3, "#c792ff"),
    ("self-reliant", "Self-Reliant", "Finish a 5+ question session with no hints", "🧭", "nohint", 1, "#8fd3ff"),
    ("hint-free-hero", "Hint-Free Hero", "Do 5 hint-free sessions", "🦉", "nohint", 5, "#8fd3ff"),
    ("explorer", "Path Finder", "Clear 25 arena levels", "🗺️", "levels", 25, "#7dffd9"),
    ("arena-master", "Arena Master", "Clear 100 arena levels", "🏆", "levels", 100, "#7dffd9"),
    ("star-collector", "Star Collector", "Earn 500 XP", "✨", "xp", 500, "#ffd36e"),
    ("supernova", "Supernova", "Earn 2000 XP", "💫", "xp", 2000, "#ffd36e"),
    ("brave-mind", "Brave Mind", "Answer 5 level-3 questions correctly", "🦁", "hard", 5, "#ff5ec8"),
    ("summit-seeker", "Summit Seeker", "Answer 20 level-3 questions correctly", "🏔️", "hard", 20, "#ff5ec8"),
]


# ---------- pure helpers ----------

def level_for_xp(total_xp):
    return int(total_xp) // XP_PER_LEVEL + 1


def level_progress(total_xp):
    total_xp = int(total_xp)
    into_level = total_xp % XP_PER_LEVEL
    return {
        "level": level_for_xp(total_xp),
        "total_xp": total_xp,
        "into_level": into_level,
        "needed": XP_PER_LEVEL,
        "percent": round(100 * into_level / XP_PER_LEVEL),
    }


def xp_for_response(xp_per_correct, difficulty, is_correct):
    if not is_correct:
        return WRONG_ANSWER_XP
    multiplier = DIFFICULTY_XP_MULTIPLIER.get(int(difficulty), 1.0)
    return round(xp_per_correct * multiplier)


def badge_is_earned(criteria_type, threshold, stats):
    return stats.get(criteria_type, 0) >= threshold


def rank_rows(rows):
    """rows: iterable of (user_id, username, total_xp, accuracy_0_to_1).
    Sorted by XP, then accuracy, then username so ties are stable."""
    return sorted(rows, key=lambda r: (-r[2], -r[3], r[1]))


def rank_change(previous_rank, current_rank):
    """Positive = moved up, negative = moved down, None = brand new on the board."""
    if not previous_rank:
        return None
    return previous_rank - current_rank


# ---------- ORM helpers ----------

def ensure_player_xp(user):
    from .models import PlayerXP
    profile, _ = PlayerXP.objects.get_or_create(user=user)
    return profile


def add_xp(user, amount):
    profile = ensure_player_xp(user)
    profile.total_xp = F("total_xp") + int(amount)
    profile.save(update_fields=["total_xp", "updated_at"])
    profile.refresh_from_db()
    return profile.total_xp


def player_stats(user):
    from .models import GameSession, GameResponse, LevelProgress
    sessions = GameSession.objects.filter(patient=user, completed=True)
    sessions_count = sessions.count()
    scored = sessions.filter(total_questions__gte=5)
    return {
        "sessions": sessions_count,
        "correct": sessions.aggregate(total=Sum("correct_answers"))["total"] or 0,
        "streak": max(sessions.values_list("best_streak", flat=True), default=0),
        "level": level_for_xp(ensure_player_xp(user).total_xp),
        "perfect": scored.filter(correct_answers=F("total_questions")).count(),
        "nohint": scored.filter(hints_used=0).count(),
        "levels": LevelProgress.objects.filter(user=user, cleared=True).count(),
        "xp": ensure_player_xp(user).total_xp,
        "hard": GameResponse.objects.filter(session__patient=user, is_correct=True,
                                            question__difficulty=3).count(),
    }


def evaluate_badges(user):
    """Award any badge whose rule is now satisfied. Returns the list of newly earned badges."""
    from .models import Badge, PlayerBadge
    stats = player_stats(user)
    earned_ids = set(PlayerBadge.objects.filter(user=user).values_list("badge_id", flat=True))
    newly = []
    for badge in Badge.objects.all():
        if badge.id in earned_ids or not badge_is_earned(badge.criteria_type, badge.threshold, stats):
            continue
        PlayerBadge.objects.create(user=user, badge=badge)
        if badge.xp_reward:
            add_xp(user, badge.xp_reward)
        newly.append(badge)
    return newly


def domain_scores(user, window=None):
    """Accuracy per radar domain (0-100). window limits to the most recent N answers."""
    from .models import GameResponse
    scores = {}
    for domain in RADAR_DOMAINS:
        qs = GameResponse.objects.filter(session__patient=user, question__domain=domain).order_by("-created_at")
        answers = [r.is_correct for r in (qs[:window] if window else qs)]
        scores[domain] = round(100 * sum(answers) / len(answers)) if answers else 0
    return scores


def skill_map(user):
    """Current skill (0-100) for every domain, with the starting value for unseen domains."""
    from .models import PlayerSkill
    stored = dict(PlayerSkill.objects.filter(user=user).values_list("domain", "score"))
    return {d: float(stored.get(d, INITIAL_SKILL)) for d in DOMAINS}


def overall_skill(user):
    """Average skill across domains, scaled 0-1. Feeds the decision tree."""
    skills = skill_map(user)
    return round(sum(skills.values()) / len(skills) / 100, 3)


def update_skill(user, domain, correct, difficulty, used_hint):
    """Move one domain's skill toward the outcome of an answer. Returns the new score."""
    from .models import PlayerSkill
    obj, _ = PlayerSkill.objects.get_or_create(user=user, domain=domain, defaults={"score": INITIAL_SKILL})
    if correct and not used_hint:
        outcome = 100.0
    elif correct:
        outcome = 60.0       # solved with a hint: counts, but less
    else:
        outcome = 0.0
    weight = SKILL_WEIGHT.get(int(difficulty), 1.0)
    obj.score = max(0.0, min(100.0, obj.score + SKILL_RATE * weight * (outcome - obj.score)))
    obj.save()
    return round(obj.score, 1)


def refresh_leaderboard():
    """Recompute ranks for every patient and remember the previous rank for arrows."""
    from .models import GameSession, LeaderboardEntry
    rows = []
    for user in User.objects.filter(is_staff=False):
        xp = ensure_player_xp(user).total_xp
        sessions = GameSession.objects.filter(patient=user, completed=True)
        total_q = sessions.aggregate(total=Sum("total_questions"))["total"] or 0
        correct = sessions.aggregate(total=Sum("correct_answers"))["total"] or 0
        accuracy = (correct / total_q) if total_q else 0.0
        rows.append((user.id, user.username, xp, accuracy, sessions.count(), accuracy))

    previous = dict(LeaderboardEntry.objects.values_list("user_id", "rank"))
    ordered = rank_rows([(r[0], r[1], r[2], r[3]) for r in rows])
    detail = {r[0]: r for r in rows}
    for position, (user_id, _name, xp, accuracy) in enumerate(ordered, start=1):
        LeaderboardEntry.objects.update_or_create(
            user_id=user_id,
            defaults={
                "total_xp": xp,
                "sessions_completed": detail[user_id][4],
                "accuracy_percent": round(accuracy * 100),
                "rank": position,
                "previous_rank": previous.get(user_id, 0),
            },
        )
    return LeaderboardEntry.objects.select_related("user").order_by("rank")
