from django.urls import path
from . import api_views

urlpatterns = [
    path("questions/", api_views.questions, name="api_questions"),
    path("sessions/start/", api_views.start_session, name="api_start_session"),
    path("sessions/answer/", api_views.answer_question, name="api_answer_question"),
    path("sessions/finish/", api_views.finish_session, name="api_finish_session"),
    path("analytics/", api_views.analytics, name="api_analytics"),
    path("ml/compare/", api_views.ml_compare, name="api_ml_compare"),
    path("report.pdf", api_views.report_pdf, name="api_report_pdf"),
    path("reminders/", api_views.reminders, name="api_reminders"),
]
