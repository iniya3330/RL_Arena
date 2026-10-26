from django.urls import path
from . import api_views, admin_views

urlpatterns = [
    path("questions/", api_views.questions, name="api_questions"),
    path("sessions/start/", api_views.start_session, name="api_start_session"),
    path("sessions/answer/", api_views.answer_question, name="api_answer_question"),
    path("sessions/finish/", api_views.finish_session, name="api_finish_session"),
    path("analytics/", api_views.analytics, name="api_analytics"),
    path("ml/compare/", api_views.ml_compare, name="api_ml_compare"),
    path("ml/predict/", api_views.ml_predict, name="api_ml_predict"),
    path("report.pdf", api_views.report_pdf, name="api_report_pdf"),
    path("reminders/", api_views.reminders, name="api_reminders"),
    # RL Arena
    path("arena/levels/", api_views.arena_levels, name="api_arena_levels"),
    path("player/progress/", api_views.player_progress, name="api_player_progress"),
    path("leaderboard/", api_views.leaderboard, name="api_leaderboard"),
    path("cognitive-report/", api_views.cognitive_report, name="api_cognitive_report"),
    path("admin/players/", admin_views.admin_players_api, name="api_admin_players"),
]
