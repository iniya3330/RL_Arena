from django.contrib import admin
from .models import (PatientProfile, GameQuestion, GameSession, GameResponse, Reminder,
                     PlayerXP, Badge, PlayerBadge, LeaderboardEntry, PlayerSkill, LevelProgress)

admin.site.register(PatientProfile)
admin.site.register(GameSession)
admin.site.register(GameResponse)
admin.site.register(Reminder)


@admin.register(GameQuestion)
class GameQuestionAdmin(admin.ModelAdmin):
    list_display = ("level_number", "domain", "difficulty", "question_text", "active")
    list_filter = ("domain", "difficulty", "active")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "criteria_type", "threshold", "xp_reward")


admin.site.register(PlayerXP)
admin.site.register(PlayerBadge)
admin.site.register(LeaderboardEntry)

admin.site.register(PlayerSkill)
admin.site.register(LevelProgress)
