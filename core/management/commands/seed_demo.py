from django.core.management.base import BaseCommand
from core.models import GameQuestion, Badge
from core.gamification import BADGE_CATALOG
from core.level_bank import all_levels


class Command(BaseCommand):
    help = "Load the 200 RL Arena levels and the badge catalogue. Accounts are created by signing up."

    def handle(self, *args, **options):
        levels = all_levels()
        for level in levels:
            GameQuestion.objects.update_or_create(level_number=level["level_number"], defaults={
                "question_text": level["question_text"],
                "options": level["options"],
                "correct_answer": level["correct_answer"],
                "domain": level["domain"],
                "difficulty": level["difficulty"],
                "hint": level["hint"],
                "active": True,
            })
        # Switch off anything left over from earlier builds (unnumbered or above level 200).
        GameQuestion.objects.filter(level_number__isnull=True).update(active=False)
        GameQuestion.objects.filter(level_number__gt=len(levels)).update(active=False)

        for order, (code, name, description, icon, criteria, threshold, glow) in enumerate(BADGE_CATALOG, start=1):
            Badge.objects.update_or_create(code=code, defaults={
                "name": name, "description": description, "icon": icon, "criteria_type": criteria,
                "threshold": threshold, "glow": glow, "xp_reward": 20, "order": order,
            })

        self.stdout.write(self.style.SUCCESS(
            f"RL Arena loaded: {len(levels)} levels, {len(BADGE_CATALOG)} badges. "
            "Sign up at /signup/ (use the word 'admin' in an email to get an admin account)."
        ))
