from django.core.management.base import BaseCommand
from core.decision_tree import train_decision_tree

class Command(BaseCommand):
    help = "Generate synthetic demo data and train the CogniCare Decision Tree."

    def handle(self, *args, **options):
        model, df = train_decision_tree(save=True)
        self.stdout.write(self.style.SUCCESS(
            f"Decision Tree trained on {len(df)} synthetic examples."
        ))
        self.stdout.write("Files: core/ml_models/training_data.csv and decision_tree.pkl")
        self.stdout.write("These metrics/data are for demonstration only, not clinical validation.")
