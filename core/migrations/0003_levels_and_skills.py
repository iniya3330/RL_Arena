from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

DOMAIN_CHOICES = [
    ("memory", "Memory"), ("attention", "Attention"), ("language", "Language"),
    ("sequencing", "Sequencing"), ("reasoning", "Reasoning"), ("visual", "Visual"),
]


def retire_legacy_questions(apps, schema_editor):
    """Questions from the old game-mode bank have no level number; switch them off."""
    GameQuestion = apps.get_model("core", "GameQuestion")
    GameQuestion.objects.filter(level_number__isnull=True).update(active=False)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0002_rl_arena"),
    ]

    operations = [
        migrations.RemoveField(model_name="gamequestion", name="game_mode"),
        migrations.RemoveField(model_name="gamesession", name="game_mode"),
        migrations.DeleteModel(name="GameMode"),
        migrations.AddField(
            model_name="gamequestion",
            name="level_number",
            field=models.PositiveSmallIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterModelOptions(
            name="gamequestion",
            options={"ordering": ["level_number", "id"]},
        ),
        migrations.CreateModel(
            name="PlayerSkill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(choices=DOMAIN_CHOICES, max_length=20)),
                ("score", models.FloatField(default=30.0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name="skills", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "domain")}},
        ),
        migrations.CreateModel(
            name="LevelProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("cleared", models.BooleanField(default=False)),
                ("cleared_at", models.DateTimeField(blank=True, null=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name="progress", to="core.gamequestion")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name="level_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "question")}},
        ),
        migrations.AlterField(
            model_name="badge",
            name="criteria_type",
            field=models.CharField(choices=[
                ("sessions", "Completed sessions"), ("correct", "Total correct answers"),
                ("streak", "Best streak in one session"), ("level", "Player level"),
                ("perfect", "Perfect sessions (5+ questions)"), ("nohint", "Hint-free sessions (5+ questions)"),
                ("levels", "Arena levels cleared"), ("xp", "Total XP"),
                ("hard", "Correct answers at level 3"),
            ], max_length=20),
        ),
        migrations.RunPython(retire_legacy_questions, migrations.RunPython.noop),
    ]
