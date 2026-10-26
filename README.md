# RL Arena · CogniCare NER

RL Arena is a supportive cognitive game for older adults, with a caregiver admin panel. Every player starts the same way: **Start run**. Five warm-up rounds learn how they play, and then a **decision tree chooses each next level** from a bank of **200 levels**. Players never see the same level twice, and new levels unlock as their skill grows. There are no domain menus on the player side.

- **Backend:** Python, Django, Django REST Framework
- **ML:** scikit-learn decision trees (a level-success model that picks each level, and a band model for the caregiver preview)
- **Frontend:** HTML, CSS, vanilla JavaScript, Chart.js, WebAudio and Speech Synthesis
- **Reports:** ReportLab PDF
- **Database:** SQLite by default, MySQL-ready (`DB_ENGINE=mysql`)

> **Safety:** Educational prototype. Scores, XP, skill and badges measure game engagement only. Nothing here diagnoses a condition. Training data is synthetic.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo           # loads the 200 levels and the badges; creates no accounts
python manage.py runserver
```

Open http://127.0.0.1:8000/ and choose **Sign up**.


## Accounts

There are no demo accounts. Everyone signs up at `/signup/` and signs in at `/login/`.

| Role | Sign-up email | After sign-in |
|---|---|---|
| Player | any email | `/dashboard/`: start runs, see the current level batch, skill, badges, reminders and leaderboard |
| Admin (caregiver) | must contain the word `admin`, e.g. `nurse.admin@clinic.org` | `/admin-panel/`: every player with their accuracy, the levels they reached and their change over time |

- Sign-in checks the role: an admin email only opens the admin panel for an admin account, and a player account cannot use an admin email.
- Passwords need at least 8 characters.
- Admins can disable and re-enable player accounts. Data is kept.

## How a run works

```
Start run → 3 · 2 · 1 · GO → the engine scans for your next level and locks onto it
  ↓
Rounds 1–5  warm-up: five levels from the opening stretch, chosen per player
  ↓
Rounds 6–10 adaptive: the level-success decision tree scores every unlocked level you
            have not played yet, and picks one whose predicted success is closest to 75%
            (a small seeded tie-break among the best three keeps play varied)
  ↓
Answer → confetti or shake, floating XP, combo meter, timer ring, skill update,
         a level-clear toast
  ↓
Finish & save → level-up and new-badge messages, leaderboard refresh
```

**Why no repeats:** a level you have already played is not offered again while unplayed, unlocked levels remain. Only after that does the engine allow a retry of an uncleared level.

**Why different players get different levels:** the warm-up is seeded by player and run, the adaptive tie-break is seeded by player, run and round, and every player's skill (and so their unlocked set) changes with their answers.

## The level-success decision tree

`core/level_model.py` trains a scikit-learn `DecisionTreeClassifier` to estimate the chance that a player answers a given level correctly. Its inputs:

| Feature | Meaning |
|---|---|
| `domain_skill` | the player's skill in that level's domain (0–100) |
| `level_position` | how far along the 200 levels the level is |
| `difficulty` | band 1–3 |
| `recent_accuracy` | last five answers |
| `correct_streak` | current run of correct answers |
| `hints_used` | hints in the last five answers |
| `avg_response_seconds` | average time in the last five answers |
| `overall_skill` | average skill across all domains |

For each candidate level the engine asks the tree for the success probability and chooses the level closest to the 75% target. Levels that are too easy and too hard are both avoided. The caregiver page shows the tree's feature weights.

## The 200 levels

- `core/level_bank.py` builds all 200 levels deterministically, so the bank is reproducible.
- Each level has three options, one correct answer and a hint.
- Every question text is unique. If a generated text repeats, the next seed is used.
- Difficulty bands: levels 1–67 are band 1, 68–134 band 2, 135–200 band 3.
- Six internal domains (memory, attention, language, sequencing, reasoning, visual) rotate level by level. They drive skill and the admin view, and are not shown to players.

## Skill and unlocks

- Each domain starts at skill 30. A correct answer moves it toward 100, a correct answer with a hint toward 60, and a wrong answer toward 0. The move is weighted by difficulty.
- A level unlocks when the player's skill in its domain reaches its requirement: `(level − 1) × 100 / 200`. Level 1 needs 0 and level 200 needs 99.5.
- A level counts as **cleared** when it is answered correctly without a hint.
- Players see their overall skill and the level map. They do not see domain names.

## XP, levels and badges

- XP per correct answer = 10 × difficulty multiplier (×1.0, ×1.5, ×2.0). A wrong answer earns 2 XP.
- Finishing a run earns +25 XP, plus +40 for a flawless run of 5+ questions.
- Every 150 XP is one level, shown on an orbit ring around the avatar.
- 23 badges cover sessions, correct answers, streaks, levels, perfect and hint-free runs, total XP and level-3 answers. Earned badges glow. Locked badges are fogged and show progress.

## The run screen

- **Start run** opens the run on the whole screen, with a countdown. Leave returns to the dashboard.
- **🔊 Hear instructions** sits next to Start run. **🔊 Read aloud** inside a run reads the question and its choices.
- Read aloud picks an English voice (en-IN, then en-GB, then any English voice), can be stopped by pressing it again, and says so when the device has no voice.

## The level map

Players see only the **current batch of ten levels** and a one-line preview of the next batch, not all 200 levels at once. The batch is the one that holds the highest level unlocked so far.

## Reminders

Each reminder has a time. When that time comes, a message bubble pops up on the dashboard, with the reminder title and time. It appears while the dashboard is open, and each reminder shows once per day. Click a bubble to dismiss it.

## Game feel

- Splash intro, animated background, and a 3-2-1-GO countdown before each run
- The engine's pick is a short scan that locks onto the chosen level number
- Per-question timer ring, combo meter, floating "+XP", confetti, flash and shake
- Full-screen **badge unlock**: "Unlocked", a medal and "Congratulations!". It is the only full-screen congratulations. Level clears and level-ups use toasts.
- Badge cards with a shine sweep
- WebAudio sound effects, with a mute button that remembers the choice on this device
- Scroll reveals, press ripples and count-up numbers. All of this respects "reduce motion".

## Admin panel

- Summary cards and an accuracy spread bar
- Player list with accuracy band (80%+ high, 60–79% mid, under 60% needs support, or no answers yet), search, band filters, sorting and live refresh
- Player detail:
  - **Levels reached**: every level the player was given, with the batch, attempts, correct answers, score and last result
  - **Change over time**: the average score of the first three runs (baseline) compared with the latest three, with a run chart. This describes game performance only. It is **not a dementia assessment or diagnosis**, and should be read together with a clinician's judgement. It needs six completed runs.
  - Per-domain accuracy and skill, six-domain radar, run history, reminders and enable/disable
- CSV export and the decision-tree preview

## API

Game:
- `POST /api/sessions/start/`: starts a run, returns warm-up round 1 and the reason
- `POST /api/sessions/answer/`: feedback, XP, cleared state, the next level and its predicted success
- `POST /api/sessions/finish/`: XP, level-ups and new badges
- `GET /api/arena/levels/`: unlocked levels (no domains), cleared state, the current batch with a next-batch preview, counts and the next unlock
- `GET /api/player/progress/`: XP ring, overall skill, badges and stats
- `GET /api/leaderboard/`, `GET /api/analytics/`, `GET /api/report.pdf`
- `GET/POST /api/reminders/`: reminders with an optional `reminder_time` (HH:MM)

Admin only:
- `GET /api/admin/players/`: players with accuracy bands and the summary
- `GET /api/ml/predict/`: the band tree preview

## Project structure

```
cogni_care_ner_prototype/
├── manage.py
├── requirements.txt
├── cognicare/                 settings, urls
├── core/
│   ├── models.py              GameQuestion (level), GameSession, GameResponse, PlayerSkill,
│   │                          LevelProgress, Reminder, PlayerXP, Badge, PlayerBadge, LeaderboardEntry
│   ├── level_bank.py          200 unique levels across six internal domains
│   ├── level_model.py         level-success decision tree
│   ├── adaptive.py            warm-up, tree-driven level choice, no repeats, outcome recording
│   ├── decision_tree.py       band tree with confidence (caregiver preview)
│   ├── gamification.py        XP, skills, badges, radar, leaderboard
│   ├── accounts.py            sign-up and sign-in rules, admin-email rule, accuracy bands
│   ├── trend.py               baseline vs. latest-three-runs comparison (game performance only)
│   ├── api_views.py           game and RL Arena API
│   ├── admin_views.py         admin panel, player detail, enable/disable, CSV
│   ├── views.py               sign-in, sign-up, player dashboard
│   ├── migrations/            0001, 0002, 0003
│   └── management/commands/   seed_demo (200 levels, badges), train_decision_tree
├── templates/                 base, home, login, signup, dashboard, admin_panel, admin_user
└── static/
    ├── css/style.css          dark glassmorphism theme and motion
    └── js/                    script.js (effects), dashboard.js, admin.js, auth.js
```

## Presentation notes

**Decision tree:** "After five warm-up rounds, a decision tree estimates how likely the player is to clear each level they have unlocked. It picks the level that is closest to a fair challenge, and never repeats a level the player has played."

**Limitation:** "The training data is synthetic demonstration data. The model is not clinically validated and only demonstrates adaptive game behaviour."
