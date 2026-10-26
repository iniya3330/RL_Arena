from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_levels_and_skills"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamequestion",
            name="translations",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
