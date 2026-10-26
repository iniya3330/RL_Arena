from rest_framework import serializers
from .models import GameQuestion, Reminder, GameSession

class GameQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameQuestion
        fields = ["id", "question_text", "options", "domain", "difficulty", "hint"]

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["id", "title", "reminder_type", "reminder_time", "notes", "active", "created_at"]
        read_only_fields = ["id", "created_at"]

class GameSessionSerializer(serializers.ModelSerializer):
    score_percent = serializers.IntegerField(read_only=True)
    class Meta:
        model = GameSession
        fields = ["id", "started_at", "ended_at", "total_questions", "correct_answers", "hints_used", "average_response_seconds", "completed", "score_percent"]
