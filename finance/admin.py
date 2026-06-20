# Register your models here.
from django.contrib import admin
from .models import UserProfile, Category, Expense, Income, Budget, SavingsGoal, ChatHistory


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "monthly_income", "monthly_budget", "currency"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon", "user"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "category", "date", "input_type", "is_recurring"]
    list_filter = ["input_type", "is_recurring", "category"]
    search_fields = ["description"]


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "source", "date"]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["user", "category", "amount", "month"]


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "target_amount", "current_amount", "deadline"]


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]