from django.db import models
from django.contrib.auth.models import User

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    preferred_language = models.CharField(max_length=30, default="English")
    caregiver_name = models.CharField(max_length=100, blank=True)
    caregiver_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username

class GameQuestion(models.Model):
    DOMAIN_CHOICES = [
        ("memory", "Memory"), ("attention", "Attention"),
        ("recognition", "Recognition"), ("sequencing", "Sequencing"),
    ]
    question_text = models.CharField(max_length=500)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=200)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    difficulty = models.PositiveSmallIntegerField(default=1)
    hint = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.domain}: {self.question_text[:50]}"

class GameSession(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    hints_used = models.PositiveIntegerField(default=0)
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
