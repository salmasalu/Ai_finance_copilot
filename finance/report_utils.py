from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import date
from .models import Expense, Income, Budget, SavingsGoal, Category


def generate_pdf_report(user):
    """Generate a monthly PDF financial report."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="finance_report_{date.today()}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    today = date.today()
    month_start = today.replace(day=1)

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=20
    )
    story.append(Paragraph("💰 AI Finance Copilot", title_style))
    story.append(Paragraph(f"Monthly Report — {today.strftime('%B %Y')}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Summary
    expenses = Expense.objects.filter(user=user, date__gte=month_start)
    incomes = Income.objects.filter(user=user, date__gte=month_start)
    total_expenses = sum(e.amount for e in expenses)
    total_income = sum(i.amount for i in incomes)
    savings = total_income - total_expenses

    story.append(Paragraph("Monthly Summary", styles["Heading1"]))
    summary_data = [
        ["Metric", "Amount (₹)"],
        ["Total Income", f"₹{total_income:,.2f}"],
        ["Total Expenses", f"₹{total_expenses:,.2f}"],
        ["Net Savings", f"₹{savings:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))

    # Expense breakdown by category
    story.append(Paragraph("Expenses by Category", styles["Heading1"]))
    categories = Category.objects.filter(user=user)
    cat_data = [["Category", "Amount (₹)", "Transactions"]]
    for cat in categories:
        cat_expenses = expenses.filter(category=cat)
        if cat_expenses.exists():
            cat_total = sum(e.amount for e in cat_expenses)
            cat_data.append([
                f"{cat.icon} {cat.name}",
                f"₹{cat_total:,.2f}",
                str(cat_expenses.count())
            ])

    if len(cat_data) > 1:
        cat_table = Table(cat_data, colWidths=[3 * inch, 2 * inch, 1.5 * inch])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ]))
        story.append(cat_table)
    story.append(Spacer(1, 0.3 * inch))

    # Recent expenses
    story.append(Paragraph("Recent Expenses", styles["Heading1"]))
    recent = expenses.order_by("-date")[:10]
    exp_data = [["Date", "Category", "Description", "Amount"]]
    for exp in recent:
        exp_data.append([
            str(exp.date),
            exp.category.name if exp.category else "N/A",
            exp.description[:30] if exp.description else "-",
            f"₹{exp.amount:,.2f}"
        ])

    if len(exp_data) > 1:
        exp_table = Table(exp_data, colWidths=[1.2 * inch, 1.5 * inch, 2.5 * inch, 1.3 * inch])
        exp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11998e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(exp_table)

    # Savings Goals
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Savings Goals", styles["Heading1"]))
    goals = SavingsGoal.objects.filter(user=user)
    goals_data = [["Goal", "Target", "Saved", "Progress"]]
    for goal in goals:
        progress = min(int((goal.current_amount / goal.target_amount) * 100), 100) if goal.target_amount > 0 else 0
        goals_data.append([
            goal.name,
            f"₹{goal.target_amount:,.2f}",
            f"₹{goal.current_amount:,.2f}",
            f"{progress}%"
        ])

    if len(goals_data) > 1:
        goals_table = Table(goals_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
        goals_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7971e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(goals_table)

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f"Generated by AI Finance Copilot on {today.strftime('%d %B %Y')}",
        styles["Normal"]
    ))

    doc.build(story)
    return response