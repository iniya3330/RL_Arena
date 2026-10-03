# CogniCare NER — AI Cognitive Gaming & Memory Assistance Prototype

A runnable Django prototype for a hackathon/demo presentation. The project keeps the original technology stack:

- **Frontend:** HTML, CSS, JavaScript, Chart.js, browser Speech Synthesis API
- **Backend:** Python + Django + Django REST Framework
- **Database:** SQLite by default; MySQL configuration is already supported
- **ML:** scikit-learn Decision Tree
- **Data:** Pandas + synthetic training data
- **Reports:** ReportLab PDF

> **Safety:** This is an educational prototype. The ML model adapts game difficulty from engagement signals. It does not diagnose dementia, predict disease, or replace medical advice.

## What was changed

### ML / question engine
1. `core/decision_tree.py`
   - Generates transparent synthetic training examples.
   - Trains a `DecisionTreeClassifier`.
   - Uses:
     - recent accuracy
     - average response time
     - hints used
     - current difficulty
     - correct streak
   - Predicts the next difficulty from 1–3.
   - Automatically trains a model if a saved model is not present.

2. `core/adaptive.py`
   - The old rule-only question selection now calls the Decision Tree.
   - Selects the next `GameQuestion` using the predicted difficulty.
   - Returns a short explanation for the UI.

3. `core/management/commands/train_decision_tree.py`
   - Explicit training/data-generation command.
   - Creates:
     - `core/ml_models/training_data.csv`
     - `core/ml_models/decision_tree.pkl`

4. `core/api_views.py`
   - Returns `next_difficulty` and `adaptation_reason` after every answer.

### Backend
- `core/views.py` was completed because it was empty in the uploaded prototype.
- Email-based demo login now correctly maps to Django users.
- Patient and caregiver roles are checked.
- Dashboard and caregiver pages load real database data.

### UI
- `templates/login.html` — full game-like login experience.
- `templates/dashboard.html` — bubble/card cognitive game dashboard.
- `templates/home.html` — redesigned landing page.
- `templates/caregiver.html` — redesigned caregiver dashboard.
- `templates/base.html` — shared navigation/background.
- `static/css/style.css` — complete responsive visual system.
- `static/js/script.js` — shared JavaScript.
- `static/js/dashboard.js` — game, voice, photo preview, reminders and analytics.

## Important: models.py

No database model changes are required for the Decision Tree integration. This is intentional so you do **not** need a new migration just for the ML feature. Existing `GameSession` and `GameResponse` records already contain the signals needed by the model.

## Exact setup — Windows PowerShell

From the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py train_decision_tree
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

If PowerShell blocks activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py train_decision_tree
.\.venv\Scripts\python.exe manage.py runserver
```

## Demo login

Patient:

```text
Email: patient@cognicare.demo
Password: Care12345!
Role: Patient / older adult
```

Caregiver:

```text
Email: admin@cognicare.demo
Password: Care12345!
Role: Caregiver / administrator
```

## How the Decision Tree works

During a game:

```text
Patient answers question
        ↓
GameResponse is stored
        ↓
Recent responses are collected
        ↓
Features are calculated
        ↓
Decision Tree predicts difficulty 1 / 2 / 3
        ↓
Question with that difficulty is selected
        ↓
Next question appears
```

The UI also displays a small adaptive-engine message explaining whether the next activity became easier, harder, or stayed comfortable.

## Main API endpoints

- `GET /api/questions/`
- `POST /api/sessions/start/`
- `POST /api/sessions/answer/`
- `POST /api/sessions/finish/`
- `GET /api/analytics/`
- `GET /api/ml/compare/`
- `GET /api/report.pdf`
- `GET /api/reminders/`
- `POST /api/reminders/`

## Project structure

```text
cogni_care_ner_prototype/
│
├── manage.py
├── requirements.txt
│
├── cognicare/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── models.py
│   ├── views.py
│   ├── api_views.py
│   ├── api_urls.py
│   ├── serializers.py
│   ├── adaptive.py
│   ├── decision_tree.py
│   ├── ml_engine.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           ├── seed_demo.py
│           └── train_decision_tree.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── dashboard.html
│   └── caregiver.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── script.js
        └── dashboard.js
```

## Presentation explanation

**Decision Tree:**  
"The system uses a Decision Tree to adapt the difficulty of cognitive games. It considers recent accuracy, response time, hint usage, current difficulty and correct-answer streak. Based on these engagement signals, it selects a suitable difficulty for the next question."

**Important limitation:**  
"The training examples are synthetic demonstration data. The model is not clinically validated and is used only to demonstrate adaptive game behaviour."
