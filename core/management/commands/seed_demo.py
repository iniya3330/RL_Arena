from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import PatientProfile, GameQuestion, Reminder

QUESTIONS = [
    ("What colour is a banana?", ["Blue", "Yellow", "Purple"], "Yellow", "recognition", 1, "Think of a ripe banana."),
    ("Remember this word: Mango. Which word did you see?", ["Apple", "Mango", "Orange"], "Mango", "memory", 1, "It is a tropical fruit."),
    ("Which item is different?", ["Chair", "Table", "Banana"], "Banana", "attention", 1, "Two are furniture."),
    ("What comes next: morning, afternoon, ...?", ["Night", "Breakfast", "Yesterday"], "Night", "sequencing", 1, "Think about the end of the day."),
    ("Which is used when it rains?", ["Umbrella", "Spoon", "Pillow"], "Umbrella", "recognition", 1, "It keeps you dry."),
    ("Remember these: 2, 4, 6. What comes next?", ["7", "8", "10"], "8", "memory", 2, "Count by twos."),
    ("Which number is largest?", ["12", "8", "5"], "12", "attention", 2, "Compare the values."),
    ("Put the day after Monday in order.", ["Sunday", "Tuesday", "Friday"], "Tuesday", "sequencing", 2, "It is the second weekday."),
    ("Which object is commonly found in a kitchen?", ["Plate", "Helmet", "Shoelace"], "Plate", "recognition", 2, "It is used for serving food."),
    ("Remember: River, Tree, Sun. Which was listed?", ["Cloud", "River", "Road"], "River", "memory", 2, "Water flows in it."),
    ("Which is the odd one out?", ["Rose", "Jasmine", "Carrot"], "Carrot", "attention", 3, "Two are flowers."),
    ("What comes after 9, 10, 11?", ["12", "8", "15"], "12", "sequencing", 3, "Continue counting."),
]

class Command(BaseCommand):
    help = "Create demo accounts, questions and reminders."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(username="caregiver_demo", defaults={"email": "admin@cognicare.demo", "is_staff": True, "is_superuser": True})
        admin.email = "admin@cognicare.demo"
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Care12345!")
        admin.save()
        patient, _ = User.objects.get_or_create(username="patient_demo", defaults={"email": "patient@cognicare.demo"})
        patient.email = "patient@cognicare.demo"
        patient.set_password("Care12345!")
        patient.save()
        PatientProfile.objects.get_or_create(user=patient, defaults={"preferred_language": "English", "caregiver_name": "Family Caregiver"})
        for q, opts, answer, domain, difficulty, hint in QUESTIONS:
            GameQuestion.objects.get_or_create(question_text=q, defaults={"options": opts, "correct_answer": answer, "domain": domain, "difficulty": difficulty, "hint": hint})
        for title, kind, note in [
            ("Morning medicine", "Medicine", "Demo reminder only"),
            ("Drink a glass of water", "Daily routine", "Stay hydrated"),
            ("Family photo game", "Cognitive activity", "Play for a few minutes"),
        ]:
            Reminder.objects.get_or_create(patient=patient, title=title, defaults={"reminder_type": kind, "notes": note})
        self.stdout.write(self.style.SUCCESS("Demo data ready. Use admin@cognicare.demo or patient@cognicare.demo with password Care12345!"))
