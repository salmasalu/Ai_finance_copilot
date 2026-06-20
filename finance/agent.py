import os
import json
from groq import Groq
from datetime import date
from .models import Expense, Income, Budget, SavingsGoal, Category
from .rag_utils import retrieve_financial_tips

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_spending_summary(user) -> dict:
    """Tool 1: Get current month spending summary."""
    today = date.today()
    month_start = today.replace(day=1)

    expenses = Expense.objects.filter(user=user, date__gte=month_start)
    incomes = Income.objects.filter(user=user, date__gte=month_start)

    total_expenses = float(sum(e.amount for e in expenses))
    total_income = float(sum(i.amount for i in incomes))

    categories = Category.objects.filter(user=user)
    category_breakdown = {}
    for cat in categories:
        cat_total = float(sum(e.amount for e in expenses.filter(category=cat)))
        if cat_total > 0:
            category_breakdown[cat.name] = cat_total

    return {
        "total_expenses": total_expenses,
        "total_income": total_income,
        "savings": total_income - total_expenses,
        "category_breakdown": category_breakdown,
        "month": today.strftime("%B %Y")
    }


def get_budget_status(user) -> dict:
    """Tool 2: Get budget vs actual spending."""
    today = date.today()
    month_start = today.replace(day=1)

    budgets = Budget.objects.filter(user=user, month=month_start)
    budget_status = []

    for budget in budgets:
        spent = float(sum(
            e.amount for e in Expense.objects.filter(
                user=user,
                category=budget.category,
                date__gte=month_start
            )
        ))
        budget_amount = float(budget.amount)
        budget_status.append({
            "category": budget.category.name,
            "budget": budget_amount,
            "spent": spent,
            "remaining": budget_amount - spent,
            "over_budget": spent > budget_amount
        })

    return {"budget_status": budget_status}


def get_savings_goals(user) -> dict:
    """Tool 3: Get savings goals progress."""
    goals = SavingsGoal.objects.filter(user=user)
    goals_data = []

    for goal in goals:
        progress = float(goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        goals_data.append({
            "name": goal.name,
            "target": float(goal.target_amount),
            "saved": float(goal.current_amount),
            "progress": round(progress, 1),
            "remaining": float(goal.target_amount - goal.current_amount),
            "deadline": str(goal.deadline) if goal.deadline else "No deadline"
        })

    return {"goals": goals_data}


def get_spending_forecast(user) -> dict:
    """Tool 4: Forecast end of month spending."""
    today = date.today()
    month_start = today.replace(day=1)
    days_passed = today.day
    days_in_month = 30

    expenses = Expense.objects.filter(user=user, date__gte=month_start)
    total_so_far = float(sum(e.amount for e in expenses))

    daily_average = total_so_far / days_passed if days_passed > 0 else 0
    projected_total = daily_average * days_in_month
    days_remaining = days_in_month - days_passed

    return {
        "total_so_far": total_so_far,
        "daily_average": round(daily_average, 2),
        "projected_month_total": round(projected_total, 2),
        "days_remaining": days_remaining,
        "recommended_daily_budget": round(
            (total_so_far / days_passed) if days_passed > 0 else 0, 2
        )
    }


def detect_anomalies(user) -> dict:
    """Tool 5: Detect unusual spending patterns."""
    from sklearn.ensemble import IsolationForest
    import numpy as np

    expenses = Expense.objects.filter(user=user).order_by("-date")[:50]

    if len(expenses) < 5:
        return {"anomalies": [], "message": "Not enough data for anomaly detection"}

    amounts = np.array([float(e.amount) for e in expenses]).reshape(-1, 1)

    model = IsolationForest(contamination=0.1, random_state=42)
    predictions = model.fit_predict(amounts)

    anomalies = []
    for i, (expense, pred) in enumerate(zip(expenses, predictions)):
        if pred == -1:
            anomalies.append({
                "date": str(expense.date),
                "amount": float(expense.amount),
                "category": expense.category.name if expense.category else "Unknown",
                "description": expense.description
            })

    return {
        "anomalies": anomalies,
        "total_checked": len(expenses),
        "anomalies_found": len(anomalies)
    }
def get_financial_advice(user, query: str = "") -> dict:
    """Tool 6: Retrieve relevant financial tips and advice using RAG."""
    tips = retrieve_financial_tips(query if query else "financial advice budgeting saving")
    return {"tips": tips, "count": len(tips)}

# TOOL DEFINITIONS FOR LANGGRAPH AGENT
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_spending_summary",
            "description": "Get the user's current month spending summary including total expenses, income, savings, and category breakdown",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_budget_status",
            "description": "Get budget vs actual spending for each category this month",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_savings_goals",
            "description": "Get progress on all savings goals",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_forecast",
            "description": "Forecast end of month spending based on current daily average",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_anomalies",
            "description": "Detect unusual or anomalous spending patterns using machine learning",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_advice",
            "description": "Retrieve relevant financial tips and advice from the knowledge base using RAG",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic to search for financial advice on"
                    }
                },
                "required": []
            }
        }
    },
]

TOOL_MAP = {
    "get_spending_summary": get_spending_summary,
    "get_budget_status": get_budget_status,
    "get_savings_goals": get_savings_goals,
    "get_spending_forecast": get_spending_forecast,
    "detect_anomalies": detect_anomalies,
    "get_financial_advice": lambda user: get_financial_advice(user),
}

SYSTEM_PROMPT = """You are an AI Personal Finance Copilot — a smart, friendly financial assistant.

You help users understand their spending, manage budgets, track savings goals, and make better financial decisions.

You have access to 5 tools:
1. get_spending_summary — current month income, expenses, savings, category breakdown
2. get_budget_status — budget vs actual spending per category
3. get_savings_goals — progress on savings goals
4. get_spending_forecast — projected end of month spending
5. detect_anomalies — detect unusual spending patterns

IMPORTANT RULES:
- Always query actual data using tools before answering financial questions
- Give specific numbers from the data, not generic advice
- Be concise but helpful
- Format amounts in ₹ (Indian Rupees)
- Never give investment advice or tax advice
- Focus on budgeting, spending insights, and savings"""


def run_agent(user, user_message: str) -> str:
    """
    Run the finance agent with tool calling.
    The agent decides which tools to call based on the user's question.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # Step 1: Ask LLM which tools to use
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=1000
    )

    assistant_message = response.choices[0].message

    # Step 2: Execute tool calls if any
    if assistant_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            if tool_name in TOOL_MAP:
                tool_result = TOOL_MAP[tool_name](user)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        # Step 3: Get final response with tool results
        final_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=1000
        )
        return final_response.choices[0].message.content

    return assistant_message.content or "I couldn't process your request. Please try again."