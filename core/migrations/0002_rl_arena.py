from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

DOMAIN_CHOICES = [
    ("memory", "Memory"),
    ("attention", "Attention"),
    ("language", "Language"),
    ("sequencing", "Sequencing"),
    ("reasoning", "Reasoning"),
    ("visual", "Visual"),
]


def remap_legacy_domains(apps, schema_editor):
    """Old 'recognition' questions become 'visual' (the closest RL Arena domain)."""
    GameQuestion = apps.get_model("core", "GameQuestion")
    GameQuestion.objects.filter(domain="recognition").update(domain="visual")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GameMode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=60)),
                ("domain", models.CharField(choices=DOMAIN_CHOICES, max_length=20)),
                ("tagline", models.CharField(blank=True, max_length=120)),
                ("icon", models.CharField(default="✦", max_length=8)),
                ("accent", models.CharField(default="#8b5cf6", max_length=7)),
                ("xp_per_correct", models.PositiveSmallIntegerField(default=10)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.AlterField(
            model_name="gamequestion",
            name="domain",
            field=models.CharField(choices=DOMAIN_CHOICES, max_length=20),
        ),
        migrations.AddField(
            model_name="gamequestion",
            name="game_mode",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name="questions", to="core.gamemode"),
        ),
        migrations.AddField(
            model_name="gamesession",
            name="game_mode",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name="sessions", to="core.gamemode"),
        ),
        migrations.AddField(
            model_name="gamesession",
            name="best_streak",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="gamesession",
            name="xp_earned",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="PlayerXP",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_xp", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name="xp_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Badge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=60)),
                ("description", models.CharField(max_length=160)),
                ("icon", models.CharField(default="🏅", max_length=8)),
                ("criteria_type", models.CharField(choices=[
                    ("sessions", "Completed sessions"), ("correct", "Total correct answers"),
                    ("streak", "Best streak in one session"), ("level", "Player level"),
                    ("perfect", "Perfect sessions (5+ questions)"), ("nohint", "Hint-free sessions (5+ questions)"),
                    ("modes", "Different game modes played"), ("xp", "Total XP"),
                    ("hard", "Correct answers at level 3"),
                ], max_length=20)),
                ("threshold", models.PositiveIntegerField(default=1)),
                ("xp_reward", models.PositiveSmallIntegerField(default=20)),
                ("glow", models.CharField(default="#8b5cf6", max_length=7)),
                ("order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.CreateModel(
            name="PlayerBadge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("earned_at", models.DateTimeField(auto_now_add=True)),
                ("badge", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name="awards", to="core.badge")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name="player_badges", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "badge")}},
        ),
        migrations.CreateModel(
            name="LeaderboardEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_xp", models.PositiveIntegerField(default=0)),
                ("sessions_completed", models.PositiveIntegerField(default=0)),
                ("accuracy_percent", models.PositiveSmallIntegerField(default=0)),
                ("rank", models.PositiveIntegerField(default=0)),
                ("previous_rank", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name="leaderboard_entry", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["rank", "id"]},
        ),
        migrations.RunPython(remap_legacy_domains, migrations.RunPython.noop),
    ]
