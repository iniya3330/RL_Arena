from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="GameQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.CharField(max_length=500)),
                ("options", models.JSONField(default=list)),
                ("correct_answer", models.CharField(max_length=200)),
                ("domain", models.CharField(choices=[("memory", "Memory"), ("attention", "Attention"), ("recognition", "Recognition"), ("sequencing", "Sequencing")], max_length=20)),
                ("difficulty", models.PositiveSmallIntegerField(default=1)),
                ("hint", models.CharField(blank=True, max_length=300)),
                ("active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="GameSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("total_questions", models.PositiveIntegerField(default=0)),
                ("correct_answers", models.PositiveIntegerField(default=0)),
                ("hints_used", models.PositiveIntegerField(default=0)),
                ("average_response_seconds", models.FloatField(default=0)),
                ("completed", models.BooleanField(default=False)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="game_sessions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PatientProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("preferred_language", models.CharField(default="English", max_length=30)),
                ("caregiver_name", models.CharField(blank=True, max_length=100)),
                ("caregiver_email", models.EmailField(blank=True, max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="patient_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Reminder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("reminder_type", models.CharField(default="Daily routine", max_length=40)),
                ("reminder_time", models.TimeField(blank=True, null=True)),
                ("notes", models.CharField(blank=True, max_length=300)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reminders", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="GameResponse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer", models.CharField(blank=True, max_length=200)),
                ("is_correct", models.BooleanField(default=False)),
                ("response_seconds", models.FloatField(default=0)),
                ("used_hint", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.gamequestion")),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="responses", to="core.gamesession")),
            ],
        ),
    ]
