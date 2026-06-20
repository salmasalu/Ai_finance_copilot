from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Expense, Income, Budget, SavingsGoal, Category, ChatHistory, UserProfile


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default categories for new user
            default_categories = [
                ("Food & Dining", "🍔"),
                ("Transport", "🚗"),
                ("Shopping", "🛍️"),
                ("Entertainment", "🎬"),
                ("Health", "💊"),
                ("Utilities", "💡"),
                ("Rent", "🏠"),
                ("Education", "📚"),
                ("Other", "💰"),
            ]
            for name, icon in default_categories:
                Category.objects.create(user=user, name=name, icon=icon)
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("dashboard")
        else:
            return render(request, "finance/register.html", {"form": form})
    else:
        form = UserCreationForm()
    return render(request, "finance/register.html", {"form": form})


@login_required
def dashboard(request):
    today = date.today()
    month_start = today.replace(day=1)

    expenses = Expense.objects.filter(user=request.user, date__gte=month_start)
    incomes = Income.objects.filter(user=request.user, date__gte=month_start)

    total_expenses = sum(e.amount for e in expenses)
    total_income = sum(i.amount for i in incomes)
    savings = total_income - total_expenses

    # Category breakdown
    categories = Category.objects.filter(user=request.user)
    category_data = []
    for cat in categories:
        cat_expenses = expenses.filter(category=cat)
        total = sum(e.amount for e in cat_expenses)
        if total > 0:
            category_data.append({"name": cat.name, "icon": cat.icon, "total": float(total)})

    # Recent expenses
    recent_expenses = Expense.objects.filter(user=request.user).order_by("-created_at")[:5]

    # Savings goals
    goals = SavingsGoal.objects.filter(user=request.user)

    # Daily spending last 7 days
    daily_labels = []
    daily_amounts = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_expenses = Expense.objects.filter(user=request.user, date=day)
        day_total = sum(e.amount for e in day_expenses)
        daily_labels.append(day.strftime("%b %d"))
        daily_amounts.append(float(day_total))

    context = {
        "total_expenses": total_expenses,
        "total_income": total_income,
        "savings": savings,
        "category_data": json.dumps(category_data),
        "recent_expenses": recent_expenses,
        "goals": goals,
        "daily_labels": json.dumps(daily_labels),
        "daily_amounts": json.dumps(daily_amounts),
        "month": today.strftime("%B %Y"),
    }
    return render(request, "finance/dashboard.html", context)


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-date")
    return render(request, "finance/expense_list.html", {"expenses": expenses})


@login_required
def add_expense(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == "POST":
        amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        description = request.POST.get("description", "")
        date_val = request.POST.get("date")
        is_recurring = request.POST.get("is_recurring") == "on"

        category = Category.objects.get(id=category_id, user=request.user)
        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            description=description,
            date=date_val,
            is_recurring=is_recurring,
            input_type="manual"
        )
        messages.success(request, "Expense added successfully!")
        return redirect("expense_list")
    return render(request, "finance/add_expense.html", {"categories": categories, "today": date.today()})


@login_required
def ocr_expense(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == "POST" and request.FILES.get("receipt"):
        from .ocr_utils import extract_expense_from_receipt
        receipt = request.FILES["receipt"]
        result = extract_expense_from_receipt(receipt)
        return render(request, "finance/ocr_expense.html", {
            "categories": categories,
            "ocr_result": result,
            "today": date.today()
        })
    return render(request, "finance/ocr_expense.html", {"categories": categories, "today": date.today()})


@login_required
def add_income(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        source = request.POST.get("source")
        date_val = request.POST.get("date")
        Income.objects.create(
            user=request.user,
            amount=amount,
            source=source,
            date=date_val
        )
        messages.success(request, "Income added successfully!")
        return redirect("dashboard")
    return render(request, "finance/add_income.html", {"today": date.today()})


@login_required
def budget_view(request):
    categories = Category.objects.filter(user=request.user)
    today = date.today()
    month_start = today.replace(day=1)

    if request.method == "POST":
        category_id = request.POST.get("category")
        amount = request.POST.get("amount")
        category = Category.objects.get(id=category_id, user=request.user)
        Budget.objects.update_or_create(
            user=request.user,
            category=category,
            month=month_start,
            defaults={"amount": amount}
        )
        messages.success(request, "Budget updated!")
        return redirect("budget")

    budgets = Budget.objects.filter(user=request.user, month=month_start)
    budget_data = []
    for budget in budgets:
        spent = sum(
            e.amount for e in Expense.objects.filter(
                user=request.user,
                category=budget.category,
                date__gte=month_start
            )
        )
        budget_data.append({
            "category": budget.category,
            "budget": float(budget.amount),
            "spent": float(spent),
            "remaining": float(budget.amount - spent),
            "percentage": min(int((spent / budget.amount) * 100), 100) if budget.amount > 0 else 0
        })

    return render(request, "finance/budget.html", {
        "categories": categories,
        "budget_data": budget_data,
        "month": today.strftime("%B %Y")
    })


@login_required
def goals_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        target = request.POST.get("target_amount")
        current = request.POST.get("current_amount", 0)
        deadline = request.POST.get("deadline") or None
        SavingsGoal.objects.create(
            user=request.user,
            name=name,
            target_amount=target,
            current_amount=current,
            deadline=deadline
        )
        messages.success(request, "Goal added!")
        return redirect("goals")

    goals = SavingsGoal.objects.filter(user=request.user)
    goals_data = []
    for goal in goals:
        percentage = min(int((goal.current_amount / goal.target_amount) * 100), 100) if goal.target_amount > 0 else 0
        goals_data.append({"goal": goal, "percentage": percentage})

    return render(request, "finance/goals.html", {"goals_data": goals_data})


@login_required
def agent_chat(request):
    history = ChatHistory.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request, "finance/agent_chat.html", {"history": reversed(list(history))})


@login_required
def reports_view(request):
    if request.method == "POST":
        from .report_utils import generate_pdf_report
        response = generate_pdf_report(request.user)
        return response
    return render(request, "finance/reports.html")


@csrf_exempt
@login_required
def agent_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        from .agent import run_agent
        response = run_agent(request.user, user_message)
        ChatHistory.objects.create(
            user=request.user,
            message=user_message,
            response=response
        )
        return JsonResponse({"response": response})
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@login_required
def voice_expense(request):
    if request.method == "POST":
        data = json.loads(request.body)
        transcript = data.get("transcript", "")
        from .nlp_utils import extract_expense_from_text
        result = extract_expense_from_text(transcript)
        if result:
            categories = Category.objects.filter(user=request.user)
            category = categories.filter(name__icontains=result.get("category", "")).first()
            if not category:
                category = categories.filter(name="Other").first()
            Expense.objects.create(
                user=request.user,
                amount=result["amount"],
                category=category,
                description=transcript,
                date=date.today(),
                input_type="voice"
            )
            return JsonResponse({"success": True, "result": result})
        return JsonResponse({"success": False, "message": "Could not extract expense from text"})
    return JsonResponse({"error": "Invalid request"}, status=400)