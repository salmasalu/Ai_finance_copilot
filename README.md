# 💰 AI Personal Finance Copilot

An AI-powered personal finance assistant built with Django and PostgreSQL, featuring agentic AI reasoning, RAG-based financial advice, receipt OCR, voice expense logging, spending forecasting, anomaly detection, and automated PDF reports.

---

## What It Does

Most finance apps just track expenses. This one thinks about them. A LangGraph-style agent with 6 tools analyzes your spending patterns, checks your budget status, forecasts end-of-month expenses, detects unusual transactions using machine learning, and retrieves personalized financial advice from a RAG knowledge base — all through a conversational interface.

---

## Features

- **Agentic AI** — Groq LLaMA 3.1 with 6 tool-calling functions for multi-step financial reasoning
- **RAG Financial Advisor** — ChromaDB knowledge base with financial tips retrieved semantically
- **Receipt OCR** — Upload receipt photos, Tesseract extracts amount and category automatically
- **Voice Expense Logging** — Speak "Spent 350 on lunch", AI extracts and saves the expense
- **Spending Forecasting** — Projects end-of-month spending based on daily average
- **Anomaly Detection** — Scikit-learn Isolation Forest detects unusual spending patterns
- **Budget Tracking** — Set budgets per category, track vs actual spending with progress bars
- **Savings Goals** — Set financial goals with targets and deadlines, track progress
- **PDF Reports** — Generate monthly financial reports with ReportLab
- **Interactive Dashboard** — Chart.js visualizations for daily spending and category breakdown
- **User Authentication** — Django session-based login, register, and protected views

---

## Agent Tools

| Tool | Description |
|---|---|
| `get_spending_summary` | Current month income, expenses, savings, category breakdown |
| `get_budget_status` | Budget vs actual spending per category |
| `get_savings_goals` | Progress on all savings goals |
| `get_spending_forecast` | Projected end of month spending |
| `detect_anomalies` | Unusual spending detection via Isolation Forest |
| `get_financial_advice` | RAG retrieval from financial knowledge base |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2, Django REST Framework |
| Database | PostgreSQL (Neon) |
| AI Agent | Groq LLaMA 3.1, Tool Calling |
| RAG | ChromaDB, Sentence Transformers |
| OCR | Tesseract, Pillow |
| NLP | Groq LLM for expense extraction |
| ML | Scikit-learn Isolation Forest |
| Frontend | Django Templates, Bootstrap 5, Chart.js |
| Voice | Web Speech API |
| Reports | ReportLab |
| Deployment | Docker, docker-compose |

---

## Project Structure

```
ai-finance-copilot/
├── finance/
│   ├── models.py          # 7 database models
│   ├── views.py           # All view functions
│   ├── agent.py           # LangGraph-style agent with 6 tools
│   ├── rag_utils.py       # ChromaDB RAG pipeline
│   ├── nlp_utils.py       # LLM-based expense extraction
│   ├── ocr_utils.py       # Tesseract receipt scanning
│   ├── report_utils.py    # ReportLab PDF generation
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin configuration
│   └── templates/         # Django HTML templates
├── financecopilot/
│   ├── settings.py        # Django configuration
│   └── urls.py            # Root URL configuration
├── datasets/
│   └── financial_tips.txt # RAG knowledge base
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/salmasalu/Ai_finance_copilot
cd Ai_finance_copilot
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Install Tesseract OCR**

Download from: https://github.com/UB-Mannheim/tesseract/wiki

**5. Create `.env` file**
```
DATABASE_URL=your_neon_postgresql_connection_string
GROQ_API_KEY=your_groq_api_key
DJANGO_SECRET_KEY=your_secret_key
```

**6. Run migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
```

**7. Run the server**
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000`

---

## Database Models

- **UserProfile** — Monthly income, budget, currency settings
- **Category** — Expense categories with icons
- **Expense** — Transactions with amount, category, date, input type (manual/voice/OCR), recurring flag
- **Income** — Income entries with source
- **Budget** — Monthly budget per category
- **SavingsGoal** — Financial goals with target and current amounts
- **ChatHistory** — Agent conversation history

---

## Author

**Ummusalma P T**
Email- salmasalu667@gmail.com