"""Interface translations for RL Arena: English (en), Hindi (hi) and Tamil (ta).

Only the interface is translated: menus, buttons, instructions and messages.
Level questions, options, hints, badge names and adaptive explanations come from the
level bank and stay in English.

Pure Python (no Django imports) so it can be tested on its own.
"""

DEFAULT_LANGUAGE = "en"
LANGUAGES = {"en": "English", "hi": "हिन्दी", "ta": "தமிழ்"}
SPEECH_LANGUAGE = {"en": "en-IN", "hi": "hi-IN", "ta": "ta-IN"}

STRINGS = {
    # ---------- navigation and layout ----------
    "nav_arena": {"en": "Arena", "hi": "अरीना", "ta": "அரங்கம்"},
    "nav_admin": {"en": "Admin panel", "hi": "एडमिन पैनल", "ta": "நிர்வாகப் பலகம்"},
    "nav_signin": {"en": "Sign in", "hi": "साइन इन करें", "ta": "உள்நுழை"},
    "nav_signup": {"en": "Sign up", "hi": "साइन अप करें", "ta": "பதிவு செய்"},
    "nav_logout": {"en": "Log out", "hi": "लॉग आउट", "ta": "வெளியேறு"},
    "sound_label": {"en": "Toggle sound effects", "hi": "ध्वनि प्रभाव चालू या बंद करें", "ta": "ஒலி விளைவுகளை மாற்று"},
    "language_label": {"en": "Language", "hi": "भाषा", "ta": "மொழி"},
    "footer_tagline": {"en": "Engagement games for supportive cognitive care · Not a diagnostic tool",
                       "hi": "सहायक संज्ञानात्मक देखभाल के लिए जुड़ाव वाले खेल · यह निदान उपकरण नहीं है",
                       "ta": "ஆதரவான அறிவாற்றல் பராமரிப்புக்கான ஈடுபாட்டு விளையாட்டுகள் · இது நோயறிதல் கருவி அல்ல"},

    # ---------- sign in ----------
    "login_eyebrow": {"en": "Welcome back", "hi": "फिर से स्वागत है", "ta": "மீண்டும் வருக"},
    "login_title": {"en": "Step back into the RL Arena", "hi": "RL Arena में फिर से आएँ", "ta": "RL Arena-க்கு மீண்டும் வாருங்கள்"},
    "login_lead": {"en": "Players go to the arena. Caregivers go to the admin panel. Both sign in with their own email and password.",
                   "hi": "खिलाड़ी अखाड़े में जाते हैं। देखभालकर्ता एडमिन पैनल में जाते हैं। दोनों अपने ईमेल और पासवर्ड से साइन इन करते हैं।",
                   "ta": "விளையாடுபவர்கள் அரங்கத்திற்குச் செல்கிறார்கள். பராமரிப்பாளர்கள் நிர்வாகப் பலகத்திற்குச் செல்கிறார்கள். இருவரும் தங்கள் மின்னஞ்சல் மற்றும் கடவுச்சொல்லால் உள்நுழைகிறார்கள்."},
    "chip_short_runs": {"en": "✓ Short runs", "hi": "✓ छोटे रन", "ta": "✓ குறுகிய ஓட்டங்கள்"},
    "chip_adaptive": {"en": "✓ Adaptive levels", "hi": "✓ अनुकूली स्तर", "ta": "✓ தகவமைப்பு நிலைகள்"},
    "chip_progress": {"en": "✓ Real-time progress", "hi": "✓ रियल-टाइम प्रगति", "ta": "✓ நேரடி முன்னேற்றம்"},
    "sign_in": {"en": "Sign in", "hi": "साइन इन करें", "ta": "உள்நுழை"},
    "good_to_see_you": {"en": "Good to see you", "hi": "आपको देखकर अच्छा लगा", "ta": "உங்களைப் பார்த்ததில் மகிழ்ச்சி"},
    "label_email": {"en": "Email", "hi": "ईमेल", "ta": "மின்னஞ்சல்"},
    "label_password": {"en": "Password", "hi": "पासवर्ड", "ta": "கடவுச்சொல்"},
    "placeholder_password": {"en": "Your password", "hi": "आपका पासवर्ड", "ta": "உங்கள் கடவுச்சொல்"},
    "enter_btn": {"en": "Enter →", "hi": "प्रवेश करें →", "ta": "நுழை →"},
    "new_here": {"en": "New here?", "hi": "नए हैं?", "ta": "புதியவரா?"},
    "create_account_link": {"en": "Create an account", "hi": "खाता बनाएँ", "ta": "கணக்கை உருவாக்கு"},
    "login_admin_hint": {"en": "<b>Admins:</b> the email must contain the word <code>admin</code>, for example <code>nurse.admin@clinic.org</code>.",
                         "hi": "<b>एडमिन:</b> ईमेल में शब्द <code>admin</code> होना चाहिए, जैसे <code>nurse.admin@clinic.org</code>।",
                         "ta": "<b>நிர்வாகிகள்:</b> மின்னஞ்சலில் <code>admin</code> என்ற சொல் இருக்க வேண்டும், எடுத்துக்காட்டாக <code>nurse.admin@clinic.org</code>."},
    "login_note": {"en": "Use real names only in production. Scores are engagement indicators, not clinical assessments.",
                   "hi": "उत्पादन में केवल असली नाम का उपयोग करें। स्कोर केवल जुड़ाव के संकेतक हैं, नैदानिक मूल्यांकन नहीं।",
                   "ta": "உற்பத்தியில் உண்மையான பெயர்களை மட்டும் பயன்படுத்துங்கள். மதிப்பெண்கள் ஈடுபாட்டின் குறியீடுகள் மட்டுமே, மருத்துவ மதிப்பீடு அல்ல."},

    # ---------- sign up ----------
    "signup_eyebrow": {"en": "Join the arena", "hi": "अखाड़े से जुड़ें", "ta": "அரங்கில் சேருங்கள்"},
    "signup_title": {"en": "Create your <span class=\"neon-text\">account</span>", "hi": "अपना <span class=\"neon-text\">खाता</span> बनाएँ", "ta": "உங்கள் <span class=\"neon-text\">கணக்கை</span> உருவாக்குங்கள்"},
    "signup_lead": {"en": "Sign up as a player to start runs and unlock levels. Caregivers sign up with an email that contains the word <code>admin</code> to reach the admin panel.",
                    "hi": "खिलाड़ी के रूप में साइन अप करें और रन शुरू करें व स्तर अनलॉक करें। देखभालकर्ता ऐसे ईमेल से साइन अप करें जिसमें <code>admin</code> शब्द हो, ताकि एडमिन पैनल तक पहुँच सकें।",
                    "ta": "விளையாட்டு ஓட்டங்களைத் தொடங்கவும் நிலைகளைத் திறக்கவும் விளையாடுபவராகப் பதிவு செய்யுங்கள். நிர்வாகப் பலகத்தை அடைய <code>admin</code> சொல் உள்ள மின்னஞ்சலுடன் பராமரிப்பாளர்கள் பதிவு செய்யுங்கள்."},
    "sign_up_card_eyebrow": {"en": "Sign up", "hi": "साइन अप", "ta": "பதிவு"},
    "sign_up_card_title": {"en": "Create an account", "hi": "खाता बनाएँ", "ta": "கணக்கை உருவாக்கு"},
    "label_name": {"en": "Full name", "hi": "पूरा नाम", "ta": "முழுப் பெயர்"},
    "password_min_hint": {"en": "(8+ characters)", "hi": "(8+ अक्षर)", "ta": "(8+ எழுத்துகள்)"},
    "label_confirm": {"en": "Confirm password", "hi": "पासवर्ड दोबारा लिखें", "ta": "கடவுச்சொல்லை உறுதிப்படுத்து"},
    "create_account_btn": {"en": "Create account →", "hi": "खाता बनाएँ →", "ta": "கணக்கை உருவாக்கு →"},
    "have_account": {"en": "Already have an account?", "hi": "पहले से खाता है?", "ta": "ஏற்கெனவே கணக்கு உள்ளதா?"},
    "sign_in_link": {"en": "Sign in", "hi": "साइन इन करें", "ta": "உள்நுழை"},
    "role_hint": {"en": "<b>Role:</b> players use any email. Admin accounts need the word <code>admin</code> in the email.",
                  "hi": "<b>भूमिका:</b> खिलाड़ी कोई भी ईमेल उपयोग कर सकते हैं। एडमिन खाते के ईमेल में <code>admin</code> शब्द होना चाहिए।",
                  "ta": "<b>பங்கு:</b> விளையாடுபவர்கள் எந்த மின்னஞ்சலையும் பயன்படுத்தலாம். நிர்வாகக் கணக்குகளின் மின்னஞ்சலில் <code>admin</code> சொல் இருக்க வேண்டும்."},

    # ---------- dashboard ----------
    "welcome_back": {"en": "Welcome back", "hi": "फिर से स्वागत है", "ta": "மீண்டும் வருக"},
    "command_deck": {"en": "Your command deck", "hi": "आपका कमांड डेक", "ta": "உங்கள் கட்டளைப் பலகம்"},
    "xp_to_next": {"en": "{xp} / {needed} XP to level {next}", "hi": "{xp} / {needed} XP, स्तर {next} तक",
                   "ta": "{xp} / {needed} XP, நிலை {next} வரை"},
    "badges_word": {"en": "badges", "hi": "बैज", "ta": "பேட்ஜ்கள்"},
    "stat_runs": {"en": "Runs", "hi": "रन", "ta": "ஓட்டங்கள்"},
    "stat_runs_sub": {"en": "completed", "hi": "पूरे हुए", "ta": "முடிந்தவை"},
    "stat_average": {"en": "Average score", "hi": "औसत स्कोर", "ta": "சராசரி மதிப்பெண்"},
    "stat_engagement": {"en": "engagement only", "hi": "केवल जुड़ाव", "ta": "ஈடுபாடு மட்டும்"},
    "stat_best_streak": {"en": "Best streak", "hi": "सर्वश्रेष्ठ सिलसिला", "ta": "சிறந்த தொடர்"},
    "stat_in_a_row": {"en": "correct in a row", "hi": "लगातार सही", "ta": "தொடர்ந்து சரியானவை"},
    "stat_reminders": {"en": "Reminders", "hi": "रिमाइंडर", "ta": "நினைவூட்டல்கள்"},
    "stat_at_time": {"en": "shown at their time", "hi": "तय समय पर दिखेंगे", "ta": "குறிப்பிட்ட நேரத்தில் காட்டப்படும்"},
    "run_eyebrow": {"en": "Arena run", "hi": "अखाड़ा रन", "ta": "அரங்க ஓட்டம்"},
    "run_title": {"en": "Play a run", "hi": "एक रन खेलें", "ta": "ஓட்டத்தை விளையாடு"},
    "ai_adaptive": {"en": "AI adaptive", "hi": "AI अनुकूली", "ta": "AI தகவமைப்பு"},
    "run_intro": {"en": "Five warm-up rounds, then the decision tree picks each next level from the levels you have unlocked. You never see the same level twice.",
                  "hi": "पाँच वार्म-अप राउंड के बाद निर्णय-वृक्ष आपके खुले स्तरों में से हर अगला स्तर चुनता है। एक ही स्तर दोबारा नहीं आता।",
                  "ta": "ஐந்து வார்ம்-அப் சுற்றுகளுக்குப் பிறகு, முடிவு மரம் உங்களின் திறக்கப்பட்ட நிலைகளிலிருந்து அடுத்த நிலையைத் தேர்ந்தெடுக்கும். ஒரே நிலை இரண்டு முறை வராது."},
    "btn_start": {"en": "▶ Start run", "hi": "▶ रन शुरू करें", "ta": "▶ ஓட்டத்தைத் தொடங்கு"},
    "btn_hear": {"en": "🔊 Hear instructions", "hi": "🔊 निर्देश सुनें", "ta": "🔊 வழிமுறைகளைக் கேள்"},
    "step_1": {"en": "Read the question. Tap the answer you think is right.", "hi": "प्रश्न पढ़ें। जो उत्तर सही लगे उस पर टैप करें।", "ta": "கேள்வியைப் படியுங்கள். சரியென நினைக்கும் விடையைத் தட்டுங்கள்."},
    "step_2": {"en": "Stuck? Tap Hint, or Read aloud to hear it.", "hi": "अटक गए? संकेत पर टैप करें, या सुनने के लिए ज़ोर से पढ़ें दबाएँ।", "ta": "சிக்கினீர்களா? குறிப்பைத் தட்டுங்கள், அல்லது கேட்க உரக்கப் படியுங்கள் என்பதை அழுத்துங்கள்."},
    "step_3": {"en": "When you are done, press Finish & save.", "hi": "हो जाने पर समाप्त करें और सहेजें दबाएँ।", "ta": "முடிந்ததும் முடித்து சேமி என்பதை அழுத்துங்கள்."},
    "batch_eyebrow": {"en": "Your levels", "hi": "आपके स्तर", "ta": "உங்கள் நிலைகள்"},
    "batch_title": {"en": "Current batch", "hi": "वर्तमान समूह", "ta": "தற்போதைய தொகுதி"},
    "batch_pill": {"en": "Batch {number} · levels {start}–{end}", "hi": "समूह {number} · स्तर {start}–{end}", "ta": "தொகுதி {number} · நிலைகள் {start}–{end}"},
    "your_skill": {"en": "Your skill", "hi": "आपका कौशल", "ta": "உங்கள் திறன்"},
    "loading_unlock": {"en": "Loading your next unlock…", "hi": "अगला अनलॉक लोड हो रहा है…", "ta": "அடுத்த திறப்பு ஏற்றப்படுகிறது…"},
    "loading_levels": {"en": "Loading levels…", "hi": "स्तर लोड हो रहे हैं…", "ta": "நிலைகள் ஏற்றப்படுகின்றன…"},
    "next_unlock": {"en": "Your next level to unlock is {level}. It needs skill {required}; you are at {current}.",
                    "hi": "आपका अगला खुलने वाला स्तर {level} है। इसके लिए कौशल {required} चाहिए; आप {current} पर हैं।",
                    "ta": "திறக்கப்பட வேண்டிய அடுத்த நிலை {level}. இதற்கு {required} திறன் தேவை; நீங்கள் {current} இல் உள்ளீர்கள்."},
    "all_unlocked": {"en": "Every level is unlocked. Keep training to clear them all.", "hi": "सभी स्तर खुल चुके हैं। सभी को पूरा करने के लिए अभ्यास जारी रखें।",
                     "ta": "எல்லா நிலைகளும் திறக்கப்பட்டுள்ளன. அனைத்தையும் முடிக்க தொடர்ந்து பயிற்சி செய்யுங்கள்."},
    "legend_cleared": {"en": "Cleared", "hi": "पूरे", "ta": "முடிந்தவை"},
    "legend_open": {"en": "Unlocked", "hi": "खुले", "ta": "திறந்தவை"},
    "legend_locked": {"en": "Locked", "hi": "बंद", "ta": "பூட்டப்பட்டவை"},
    "state_cleared": {"en": "cleared", "hi": "पूरा", "ta": "முடிந்தது"},
    "state_open": {"en": "unlocked", "hi": "खुला", "ta": "திறந்தது"},
    "state_locked": {"en": "locked", "hi": "बंद", "ta": "பூட்டப்பட்டது"},
    "next_batch": {"en": "<b>Next batch {number}</b> · levels {start}–{end}. These open as your skill grows.",
                   "hi": "<b>अगला समूह {number}</b> · स्तर {start}–{end}। ये आपके कौशल के बढ़ने के साथ खुलेंगे।",
                   "ta": "<b>அடுத்த தொகுதி {number}</b> · நிலைகள் {start}–{end}. உங்கள் திறன் வளரும்போது இவை திறக்கும்."},
    "last_batch": {"en": "<b>You have reached the last batch.</b> All {total} levels are in the arena.",
                   "hi": "<b>आप अंतिम समूह तक पहुँच गए हैं।</b> सभी {total} स्तर अखाड़े में हैं।",
                   "ta": "<b>நீங்கள் கடைசி தொகுதியை அடைந்துவிட்டீர்கள்.</b> எல்லா {total} நிலைகளும் அரங்கில் உள்ளன."},
    "badges_eyebrow": {"en": "Achievements", "hi": "उपलब्धियाँ", "ta": "சாதனைகள்"},
    "badge_wall": {"en": "Badge wall", "hi": "बैज वॉल", "ta": "பேட்ஜ் சுவர்"},
    "badges_loading": {"en": "Loading badges…", "hi": "बैज लोड हो रहे हैं…", "ta": "பேட்ஜ்கள் ஏற்றப்படுகின்றன…"},
    "unlocked_count": {"en": "{count} unlocked", "hi": "{count} अनलॉक", "ta": "{count} திறக்கப்பட்டது"},
    "earned_on": {"en": "Earned {date}", "hi": "{date} को मिला", "ta": "{date} அன்று பெற்றது"},
    "live_standings": {"en": "Live standings", "hi": "लाइव रैंकिंग", "ta": "நேரடி தரவரிசை"},
    "leaderboard": {"en": "Leaderboard", "hi": "लीडरबोर्ड", "ta": "தரவரிசைப் பட்டியல்"},
    "your_rank": {"en": "You're #{rank}", "hi": "आप #{rank} पर हैं", "ta": "நீங்கள் #{rank} இல் உள்ளீர்கள்"},
    "unranked": {"en": "Unranked", "hi": "रैंकिंग नहीं", "ta": "தரவரிசை இல்லை"},
    "you": {"en": "you", "hi": "आप", "ta": "நீங்கள்"},
    "runs_short": {"en": "runs", "hi": "रन", "ta": "ஓட்டங்கள்"},
    "standings_empty": {"en": "Standings appear after the first run.", "hi": "पहला रन पूरा होने के बाद रैंकिंग दिखेगी।", "ta": "முதல் ஓட்டத்திற்குப் பிறகு தரவரிசை தோன்றும்."},
    "loading_standings": {"en": "Loading standings…", "hi": "रैंकिंग लोड हो रही है…", "ta": "தரவரிசை ஏற்றப்படுகிறது…"},
    "reminders_eyebrow": {"en": "Daily reminders", "hi": "दैनिक रिमाइंडर", "ta": "தினசரி நினைவூட்டல்கள்"},
    "reminders_title": {"en": "Reminders", "hi": "रिमाइंडर", "ta": "நினைவூட்டல்கள்"},
    "reminders_note": {"en": "A message pops up at each reminder's time while this page is open.",
                       "hi": "जब यह पेज खुला हो, तो हर रिमाइंडर के तय समय पर एक संदेश दिखता है।",
                       "ta": "இந்தப் பக்கம் திறந்திருக்கும்போது ஒவ்வொரு நினைவூட்டலின் நேரத்திலும் ஒரு செய்தி தோன்றும்."},
    "no_reminders": {"en": "No reminders yet. Add one with a time below.", "hi": "अभी कोई रिमाइंडर नहीं है। नीचे समय के साथ एक जोड़ें।",
                     "ta": "இன்னும் நினைவூட்டல்கள் இல்லை. கீழே நேரத்துடன் ஒன்றைச் சேர்க்கவும்."},
    "any_time": {"en": "Any time", "hi": "कभी भी", "ta": "எந்த நேரமும்"},
    "reminder_placeholder": {"en": "e.g. Take morning medicine", "hi": "जैसे: सुबह की दवा लें", "ta": "எ.கா. காலை மருந்து எடு"},
    "reminder_text_label": {"en": "Reminder text", "hi": "रिमाइंडर का पाठ", "ta": "நினைவூட்டல் உரை"},
    "reminder_type_label": {"en": "Reminder type", "hi": "रिमाइंडर का प्रकार", "ta": "நினைவூட்டல் வகை"},
    "reminder_time_label": {"en": "Reminder time", "hi": "रिमाइंडर का समय", "ta": "நினைவூட்டல் நேரம்"},
    "add_reminder": {"en": "＋ Add reminder", "hi": "＋ रिमाइंडर जोड़ें", "ta": "＋ நினைவூட்டல் சேர்"},
    "type_daily": {"en": "Daily routine", "hi": "दैनिक दिनचर्या", "ta": "தினசரி வழக்கம்"},
    "type_medicine": {"en": "Medicine", "hi": "दवा", "ta": "மருந்து"},
    "type_cognitive": {"en": "Cognitive activity", "hi": "संज्ञानात्मक गतिविधि", "ta": "அறிவாற்றல் செயல்பாடு"},
    "type_appointment": {"en": "Appointment", "hi": "अपॉइंटमेंट", "ta": "சந்திப்பு"},
    "reminder_prefix": {"en": "Reminder:", "hi": "रिमाइंडर:", "ta": "நினைவூட்டல்:"},
    "progress_eyebrow": {"en": "Your journey", "hi": "आपकी यात्रा", "ta": "உங்கள் பயணம்"},
    "score_history": {"en": "Score history", "hi": "स्कोर इतिहास", "ta": "மதிப்பெண் வரலாறு"},
    "export_report": {"en": "Export report ↓", "hi": "रिपोर्ट निर्यात करें ↓", "ta": "அறிக்கையை ஏற்றுமதி செய் ↓"},
    "col_date": {"en": "Date", "hi": "तारीख", "ta": "தேதி"},
    "col_score": {"en": "Score", "hi": "स्कोर", "ta": "மதிப்பெண்"},
    "col_questions": {"en": "Questions", "hi": "प्रश्न", "ta": "கேள்விகள்"},
    "col_hints": {"en": "Hints", "hi": "संकेत", "ta": "குறிப்புகள்"},
    "col_best_streak": {"en": "Best streak", "hi": "सर्वश्रेष्ठ सिलसिला", "ta": "சிறந்த தொடர்"},
    "history_empty": {"en": "Finish your first run and it will appear here.", "hi": "पहला रन पूरा करें, तो यह यहाँ दिखेगा।",
                      "ta": "முதல் ஓட்டத்தை முடியுங்கள், அது இங்கு தோன்றும்."},

    # ---------- run screen ----------
    "level_badge": {"en": "LV {n}", "hi": "स्तर {n}", "ta": "நிலை {n}"},
    "level_label": {"en": "Level {n}", "hi": "स्तर {n}", "ta": "நிலை {n}"},
    "round_label": {"en": "Round {number} of {total} · {phase}", "hi": "राउंड {number} / {total} · {phase}", "ta": "சுற்று {number} / {total} · {phase}"},
    "phase_warmup": {"en": "Warm-up", "hi": "वार्म-अप", "ta": "வார்ம்-அப்"},
    "phase_adaptive": {"en": "Adaptive", "hi": "अनुकूली", "ta": "தகவமைப்பு"},
    "streak_label": {"en": "🔥 {n} streak", "hi": "🔥 {n} सिलसिला", "ta": "🔥 {n} தொடர்"},
    "xp_label": {"en": "+{n} XP", "hi": "+{n} XP", "ta": "+{n} XP"},
    "leave_btn": {"en": "✕ Leave", "hi": "✕ छोड़ें", "ta": "✕ வெளியேறு"},
    "hint_btn": {"en": "💡 Hint", "hi": "💡 संकेत", "ta": "💡 குறிப்பு"},
    "read_aloud_btn": {"en": "🔊 Read aloud", "hi": "🔊 ज़ोर से पढ़ें", "ta": "🔊 உரக்கப் படி"},
    "finish_btn": {"en": "Finish & save", "hi": "समाप्त करें और सहेजें", "ta": "முடித்து சேமி"},
    "engine_title": {"en": "Adaptive engine", "hi": "अनुकूली इंजन", "ta": "தகவமைப்பு இயந்திரம்"},
    "engine_calibrating": {"en": "Calibration is learning how you play.", "hi": "कैलिब्रेशन सीख रहा है कि आप कैसे खेलते हैं।",
                           "ta": "நீங்கள் எப்படி விளையாடுகிறீர்கள் என்பதை அளவுத்திருத்தம் கற்றுக்கொள்கிறது."},
    "hint_default": {"en": "Take your time. Think about the clue.", "hi": "समय लें। सुराग पर सोचें।", "ta": "நிதானமாக யோசியுங்கள். துப்பைப் பற்றி சிந்தியுங்கள்."},
    "getting_question": {"en": "Getting your first question…", "hi": "पहला प्रश्न लाया जा रहा है…", "ta": "முதல் கேள்வி பெறப்படுகிறது…"},
    "run_complete": {"en": "Run complete. Wonderful effort ✨", "hi": "रन पूरा हुआ। शानदार प्रयास ✨", "ta": "ஓட்டம் முடிந்தது. அருமையான முயற்சி ✨"},
    "press_finish": {"en": "Press Finish & save to bank your XP.", "hi": "अपने XP सहेजने के लिए समाप्त करें और सहेजें दबाएँ।",
                     "ta": "உங்கள் XP ஐ சேமிக்க முடித்து சேமி என்பதை அழுத்துங்கள்."},
    "no_more_levels": {"en": "No more levels available right now.", "hi": "अभी और स्तर उपलब्ध नहीं हैं।", "ta": "இப்போது வேறு நிலைகள் இல்லை."},
    "predicted": {"en": "Predicted success for the next level: {pct}%", "hi": "अगले स्तर पर अनुमानित सफलता: {pct}%", "ta": "அடுத்த நிலையில் கணிக்கப்பட்ட வெற்றி: {pct}%"},
    "feedback_correct": {"en": "Well done! Let's try another.", "hi": "शाबाश! एक और कोशिश करें।", "ta": "சபாஷ்! இன்னொன்றை முயற்சிப்போம்."},
    "feedback_wrong": {"en": "Good try. Let's practise together.", "hi": "अच्छी कोशिश। आइए मिलकर अभ्यास करें।", "ta": "நல்ல முயற்சி. சேர்ந்து பயிற்சி செய்வோம்."},
    "score_line": {"en": "Score {pct}% · +{xp} XP", "hi": "स्कोर {pct}% · +{xp} XP", "ta": "மதிப்பெண் {pct}% · +{xp} XP"},
    "not_quite": {"en": "Not quite", "hi": "सही नहीं", "ta": "சரியில்லை"},
    "level_cleared_toast": {"en": "Level {n} cleared! Higher levels are opening.", "hi": "स्तर {n} पूरा हुआ! उच्च स्तर खुल रहे हैं।",
                            "ta": "நிலை {n} முடிந்தது! உயர் நிலைகள் திறக்கின்றன."},
    "run_saved": {"en": "Run saved · +{xp} XP", "hi": "रन सहेजा गया · +{xp} XP", "ta": "ஓட்டம் சேமிக்கப்பட்டது · +{xp} XP"},
    "flawless": {"en": "Flawless run! Bonus XP earned.", "hi": "निर्दोष रन! बोनस XP मिला।", "ta": "குறையற்ற ஓட்டம்! போனஸ் XP கிடைத்தது."},
    "reached_level": {"en": "You reached level {n}!", "hi": "आप स्तर {n} पर पहुँचे!", "ta": "நீங்கள் நிலை {n}ஐ அடைந்தீர்கள்!"},
    "unlocked": {"en": "Unlocked", "hi": "अनलॉक हुआ", "ta": "திறக்கப்பட்டது"},
    "congratulations": {"en": "Congratulations!", "hi": "बधाई हो!", "ta": "வாழ்த்துக்கள்!"},
    "continue_btn": {"en": "Continue", "hi": "जारी रखें", "ta": "தொடரவும்"},
    "leave_confirm": {"en": "Leave this run? Answers so far are saved only when you press Finish.",
                      "hi": "क्या यह रन छोड़ें? अब तक के उत्तर केवल समाप्त करें दबाने पर सहेजे जाएँगे।",
                      "ta": "இந்த ஓட்டத்தை விட்டு வெளியேறவா? இதுவரையான விடைகள் முடித்து சேமி அழுத்தும்போது மட்டுமே சேமிக்கப்படும்."},
    "could_not_start": {"en": "Could not start: {error}", "hi": "शुरू नहीं हो सका: {error}", "ta": "தொடங்க முடியவில்லை: {error}"},
    "could_not_add_reminder": {"en": "Could not add reminder: {error}", "hi": "रिमाइंडर जोड़ नहीं सका: {error}", "ta": "நினைவூட்டலைச் சேர்க்க முடியவில்லை: {error}"},
    "tts_unsupported": {"en": "Read aloud is not supported in this browser. Try Chrome, Edge or Safari.",
                        "hi": "इस ब्राउज़र में ज़ोर से पढ़ना समर्थित नहीं है। Chrome, Edge या Safari आज़माएँ।",
                        "ta": "இந்த உலாவியில் உரக்கப் படித்தல் ஆதரவில்லை. Chrome, Edge அல்லது Safari ஐ முயற்சிக்கவும்."},
    "tts_failed": {"en": "Read aloud could not start on this device.", "hi": "इस डिवाइस पर ज़ोर से पढ़ना शुरू नहीं हो सका।",
                   "ta": "இந்தச் சாதனத்தில் உரக்கப் படித்தல் தொடங்க முடியவில்லை."},
    "tts_no_voice": {"en": "This device has no voice for this language, so read aloud is unavailable.",
                     "hi": "इस डिवाइस पर इस भाषा की आवाज़ नहीं है, इसलिए ज़ोर से पढ़ना उपलब्ध नहीं है।",
                     "ta": "இந்தச் சாதனத்தில் இந்த மொழிக்கான குரல் இல்லை, அதனால் உரக்கப் படித்தல் கிடைக்கவில்லை."},
    "start_run_first": {"en": "Start a run first, then the question can be read aloud.", "hi": "पहले रन शुरू करें, फिर प्रश्न ज़ोर से पढ़ा जा सकता है।",
                        "ta": "முதலில் ஓட்டத்தைத் தொடங்குங்கள், பிறகு கேள்வியை உரக்கப் படிக்கலாம்."},
    "instructions": {"en": "Welcome to RL Arena. Press Start run. A countdown will show, then a question with answer choices. Tap the answer you think is right. If you are stuck, tap Hint, or Read aloud to hear the question again. When you are finished, press Finish and save.",
                     "hi": "RL Arena में आपका स्वागत है। रन शुरू करें दबाएँ। उल्टी गिनती दिखेगी, फिर उत्तर विकल्पों वाला प्रश्न आएगा। जो उत्तर सही लगे उस पर टैप करें। अटकें तो संकेत पर टैप करें, या प्रश्न दोबारा सुनने के लिए ज़ोर से पढ़ें दबाएँ। पूरा होने पर समाप्त करें और सहेजें दबाएँ।",
                     "ta": "RL Arena-க்கு வரவேற்கிறோம். ஓட்டத்தைத் தொடங்கு என்பதை அழுத்துங்கள். கவுண்ட்டவுன் காட்டப்படும், பிறகு விடை விருப்பங்களுடன் கேள்வி வரும். சரியென நினைக்கும் விடையைத் தட்டுங்கள். சிக்கினால், குறிப்பைத் தட்டுங்கள், அல்லது கேள்வியை மீண்டும் கேட்க உரக்கப் படியுங்கள். முடிந்ததும் முடித்து சேமி என்பதை அழுத்துங்கள்."},
    "read_question_prefix": {"en": "{question} The choices are: {choices}.", "hi": "{question} विकल्प हैं: {choices}।", "ta": "{question} விருப்பங்கள்: {choices}."},
}


def get_language(request):
    """The language chosen in this browser session, or English."""
    code = None
    if request is not None and hasattr(request, "session"):
        code = request.session.get("lang")
    return code if code in LANGUAGES else DEFAULT_LANGUAGE


def text(key, lang=DEFAULT_LANGUAGE, **values):
    """One translated string. Falls back to English, then to the key itself."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    template = entry.get(lang) or entry[DEFAULT_LANGUAGE]
    return template.format(**values) if values else template


def strings_for(lang):
    """Every string in one language, for the dashboard script."""
    return {key: (entry.get(lang) or entry[DEFAULT_LANGUAGE]) for key, entry in STRINGS.items()}


# ---------- answer feedback, sign-up helpers and badges ----------

STRINGS.update({
    "feedback_correct": {"en": "Well done! Let's try another.", "hi": "शाबाश! एक और कोशिश करें।",
                         "ta": "நன்று! இன்னொன்றை முயற்சி செய்யுங்கள்."},
    "feedback_wrong": {"en": "Good try. Let's practise together.", "hi": "अच्छी कोशिश। आइए मिलकर अभ्यास करें।",
                       "ta": "நல்ல முயற்சி. சேர்ந்து பயிற்சி செய்வோம்."},
    "passwords_mismatch": {"en": "Passwords do not match", "hi": "पासवर्ड मेल नहीं खाते",
                           "ta": "கடவுச்சொற்கள் பொருந்தவில்லை"},
    "hint_admin_account": {"en": "<b>Admin account:</b> this email opens the admin panel and the player list with accuracy.",
                           "hi": "<b>एडमिन खाता:</b> यह ईमेल एडमिन पैनल और सटीकता के साथ खिलाड़ी सूची खोलता है।",
                           "ta": "<b>நிர்வாகக் கணக்கு:</b> இந்த மின்னஞ்சல் நிர்வாகப் பலகத்தையும் துல்லியத்துடன் கூடிய விளையாடுபவர் பட்டியலையும் திறக்கும்."},
    "hint_player_account": {"en": "<b>Player account:</b> this email opens your arena. Add the word <code>admin</code> to the email for a caregiver account.",
                            "hi": "<b>खिलाड़ी खाता:</b> यह ईमेल आपका अखाड़ा खोलता है। देखभालकर्ता खाते के लिए ईमेल में <code>admin</code> शब्द जोड़ें।",
                            "ta": "<b>விளையாடுபவர் கணக்கு:</b> இந்த மின்னஞ்சல் உங்கள் அரங்கைத் திறக்கும். பராமரிப்பாளர் கணக்கிற்கு மின்னஞ்சலில் <code>admin</code> சொல்லைச் சேருங்கள்."},
})

# Badge names and descriptions, by badge code. English comes from gamification.BADGE_CATALOG.
BADGE_TEXT = {
    "first-steps": {"hi": ("पहला कदम", "अपना पहला सत्र पूरा करें"), "ta": ("முதல் அடி", "உங்கள் முதல் அமர்வை முடியுங்கள்")},
    "regular-racer": {"hi": ("नियमित धावक", "5 सत्र पूरे करें"), "ta": ("தொடர் ஓட்டக்காரர்", "5 அமர்வுகளை முடியுங்கள்")},
    "arena-veteran": {"hi": ("अखाड़े का अनुभवी", "10 सत्र पूरे करें"), "ta": ("அரங்க அனுபவசாலி", "10 அமர்வுகளை முடியுங்கள்")},
    "iron-routine": {"hi": ("लौह अभ्यास", "25 सत्र पूरे करें"), "ta": ("இரும்பு வழக்கம்", "25 அமர்வுகளை முடியுங்கள்")},
    "sharp-start": {"hi": ("तेज़ शुरुआत", "10 प्रश्नों के सही उत्तर दें"), "ta": ("சுறுசுறுப்பான தொடக்கம்", "10 கேள்விகளுக்குச் சரியாக விடையளியுங்கள்")},
    "quick-mind": {"hi": ("तेज़ दिमाग़", "50 प्रश्नों के सही उत्तर दें"), "ta": ("விரைவு மூளை", "50 கேள்விகளுக்குச் சரியாக விடையளியுங்கள்")},
    "century-club": {"hi": ("शतक क्लब", "100 प्रश्नों के सही उत्तर दें"), "ta": ("சதக் கழகம்", "100 கேள்விகளுக்குச் சரியாக விடையளியுங்கள்")},
    "hot-streak": {"hi": ("गर्म सिलसिला", "लगातार 3 सही उत्तर पाएँ"), "ta": ("சூடான தொடர்", "தொடர்ச்சியாக 3 சரியான விடைகள்")},
    "on-fire": {"hi": ("जोश में", "लगातार 5 सही उत्तर पाएँ"), "ta": ("தீப்பிடித்த", "தொடர்ச்சியாக 5 சரியான விடைகள்")},
    "unstoppable": {"hi": ("अजेय", "लगातार 8 सही उत्तर पाएँ"), "ta": ("தடுக்க முடியாத", "தொடர்ச்சியாக 8 சரியான விடைகள்")},
    "rising-star": {"hi": ("उभरता सितारा", "स्तर 2 तक पहुँचें"), "ta": ("உதய நட்சத்திரம்", "நிலை 2-ஐ அடையுங்கள்")},
    "orbit-runner": {"hi": ("कक्षा धावक", "स्तर 5 तक पहुँचें"), "ta": ("சுற்றுப்பாதை ஓட்டக்காரர்", "நிலை 5-ஐ அடையுங்கள்")},
    "galaxy-guide": {"hi": ("आकाशगंगा मार्गदर्शक", "स्तर 10 तक पहुँचें"), "ta": ("விண்மீன் வழிகாட்டி", "நிலை 10-ஐ அடையுங்கள்")},
    "flawless-round": {"hi": ("निर्दोष दौर", "5+ प्रश्नों के सत्र में 100% स्कोर करें"), "ta": ("குறையற்ற சுற்று", "5+ கேள்விகள் கொண்ட அமர்வில் 100% மதிப்பெண் பெறுங்கள்")},
    "perfectionist": {"hi": ("पूर्णतावादी", "3 सत्रों में 100% स्कोर करें"), "ta": ("முழுமையாளர்", "3 அமர்வுகளில் 100% மதிப்பெண் பெறுங்கள்")},
    "self-reliant": {"hi": ("आत्मनिर्भर", "बिना संकेत के 5+ प्रश्नों का सत्र पूरा करें"), "ta": ("தன்னம்பிக்கையாளர்", "குறிப்பின்றி 5+ கேள்விகள் கொண்ட அமர்வை முடியுங்கள்")},
    "hint-free-hero": {"hi": ("संकेत-मुक्त नायक", "5 बिना-संकेत सत्र करें"), "ta": ("குறிப்பில்லா வீரர்", "5 குறிப்பில்லா அமர்வுகளை முடியுங்கள்")},
    "explorer": {"hi": ("राह खोजी", "अखाड़े के 25 स्तर पार करें"), "ta": ("பாதை தேடுபவர்", "அரங்க நிலைகள் 25-ஐ முடியுங்கள்")},
    "arena-master": {"hi": ("अखाड़ा विजेता", "अखाड़े के 100 स्तर पार करें"), "ta": ("அரங்க மாஸ்டர்", "அரங்க நிலைகள் 100-ஐ முடியுங்கள்")},
    "star-collector": {"hi": ("सितारा संग्राहक", "500 XP कमाएँ"), "ta": ("நட்சத்திரச் சேகரிப்பாளர்", "500 XP பெறுங்கள்")},
    "supernova": {"hi": ("सुपरनोवा", "2000 XP कमाएँ"), "ta": ("சூப்பர்நோவா", "2000 XP பெறுங்கள்")},
    "brave-mind": {"hi": ("साहसी मन", "स्तर-3 के 5 प्रश्नों के सही उत्तर दें"), "ta": ("துணிவான மனம்", "நிலை-3 கேள்விகள் 5-க்குச் சரியாக விடையளியுங்கள்")},
    "summit-seeker": {"hi": ("शिखर खोजी", "स्तर-3 के 20 प्रश्नों के सही उत्तर दें"), "ta": ("சிகரத் தேடுபவர்", "நிலை-3 கேள்விகள் 20-க்குச் சரியாக விடையளியுங்கள்")},
}


def badge_text(code, lang, name, description):
    """Translated badge name and description, or the English ones."""
    if lang in ("hi", "ta") and code in BADGE_TEXT and lang in BADGE_TEXT[code]:
        return BADGE_TEXT[code][lang]
    return name, description
