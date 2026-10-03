from django.contrib import admin
from .models import PatientProfile, GameQuestion, GameSession, GameResponse, Reminder

admin.site.register(PatientProfile)
admin.site.register(GameQuestion)
admin.site.register(GameSession)
admin.site.register(GameResponse)
admin.site.register(Reminder)
