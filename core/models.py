from django.db import models
from django.contrib.auth.models import User

# Shared domain list. The six RL Arena domains drive the cognitive radar chart.
DOMAIN_CHOICES = [
    ("memory", "Memory"),
    ("attention", "Attention"),
    ("language", "Language"),
    ("sequencing", "Sequencing"),
    ("reasoning", "Reasoning"),
    ("visual", "Visual"),
]


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    preferred_language = models.CharField(max_length=30, default="English")
    caregiver_name = models.CharField(max_length=100, blank=True)
    caregiver_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class GameQuestion(models.Model):
    DOMAIN_CHOICES = DOMAIN_CHOICES

    question_text = models.CharField(max_length=500)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=200)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    difficulty = models.PositiveSmallIntegerField(default=1)
    hint = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=True)
    level_number = models.PositiveSmallIntegerField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ["level_number", "id"]

    def __str__(self):
        return f"L{self.level_number} {self.domain}: {self.question_text[:50]}"


class GameSession(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    hints_used = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    average_response_seconds = models.FloatField(default=0)
    completed = models.BooleanField(default=False)

    @property
    def score_percent(self):
        return round((self.correct_answers / self.total_questions) * 100) if self.total_questions else 0


class GameResponse(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(GameQuestion, on_delete=models.PROTECT)
    answer = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField(default=False)
    response_seconds = models.FloatField(default=0)
    used_hint = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class PlayerSkill(models.Model):
    """Skill score (0-100) per domain. Unlocks levels whose requirement it meets."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    score = models.FloatField(default=30.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "domain")]


class LevelProgress(models.Model):
    """A player's record on one level: attempts and whether it was cleared."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="level_progress")
    question = models.ForeignKey(GameQuestion, on_delete=models.CASCADE, related_name="progress")
    attempts = models.PositiveIntegerField(default=0)
    cleared = models.BooleanField(default=False)
    cleared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("user", "question")]


class Reminder(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reminders")
    title = models.CharField(max_length=150)
    reminder_type = models.CharField(max_length=40, default="Daily routine")
    reminder_time = models.TimeField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PlayerXP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="xp_profile")
    total_xp = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.total_xp} XP"


class Badge(models.Model):
    CRITERIA_CHOICES = [
        ("sessions", "Completed sessions"),
        ("correct", "Total correct answers"),
        ("streak", "Best streak in one session"),
        ("level", "Player level"),
        ("perfect", "Perfect sessions (5+ questions)"),
        ("nohint", "Hint-free sessions (5+ questions)"),
        ("levels", "Arena levels cleared"),
        ("xp", "Total XP"),
        ("hard", "Correct answers at level 3"),
    ]
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=160)
    icon = models.CharField(max_length=8, default="🏅")
    criteria_type = models.CharField(max_length=20, choices=CRITERIA_CHOICES)
    threshold = models.PositiveIntegerField(default=1)
    xp_reward = models.PositiveSmallIntegerField(default=20)
    glow = models.CharField(max_length=7, default="#8b5cf6")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class PlayerBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awards")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "badge")]


class LeaderboardEntry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="leaderboard_entry")
    total_xp = models.PositiveIntegerField(default=0)
    sessions_completed = models.PositiveIntegerField(default=0)
    accuracy_percent = models.PositiveSmallIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)
    previous_rank = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rank", "id"]
