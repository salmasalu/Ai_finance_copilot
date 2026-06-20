from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.add_expense, name="add_expense"),
    path("expenses/ocr/", views.ocr_expense, name="ocr_expense"),
    path("income/add/", views.add_income, name="add_income"),
    path("budget/", views.budget_view, name="budget"),
    path("goals/", views.goals_view, name="goals"),
    path("agent/", views.agent_chat, name="agent_chat"),
    path("reports/", views.reports_view, name="reports"),
    path("api/agent/", views.agent_api, name="agent_api"),
    path("api/voice/", views.voice_expense, name="voice_expense"),
]