import re
import os
from groq import Groq
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CATEGORY_MAP = {
    "food": "Food & Dining",
    "lunch": "Food & Dining",
    "dinner": "Food & Dining",
    "breakfast": "Food & Dining",
    "restaurant": "Food & Dining",
    "cafe": "Food & Dining",
    "coffee": "Food & Dining",
    "tea": "Food & Dining",
    "grocery": "Food & Dining",
    "groceries": "Food & Dining",
    "auto": "Transport",
    "bus": "Transport",
    "train": "Transport",
    "taxi": "Transport",
    "uber": "Transport",
    "ola": "Transport",
    "petrol": "Transport",
    "fuel": "Transport",
    "transport": "Transport",
    "movie": "Entertainment",
    "netflix": "Entertainment",
    "amazon": "Entertainment",
    "entertainment": "Entertainment",
    "medicine": "Health",
    "doctor": "Health",
    "hospital": "Health",
    "pharmacy": "Health",
    "health": "Health",
    "electricity": "Utilities",
    "water": "Utilities",
    "internet": "Utilities",
    "phone": "Utilities",
    "rent": "Rent",
    "book": "Education",
    "course": "Education",
    "education": "Education",
    "shopping": "Shopping",
    "clothes": "Shopping",
}


def extract_expense_from_text(text: str) -> dict:
    """
    Extract expense details from natural language text using Groq LLM.
    Example: "spent 350 on lunch" → {"amount": 350, "category": "Food & Dining"}
    """
    try:
        prompt = f"""Extract expense information from this text and return ONLY a JSON object.
Text: "{text}"

Return exactly this format:
{{"amount": <number>, "category": "<category>", "description": "<brief description>"}}

Categories to choose from: Food & Dining, Transport, Shopping, Entertainment, Health, Utilities, Rent, Education, Other

If you cannot find an amount, return null for amount.
Return ONLY the JSON, no explanation."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
        )

        result_text = response.choices[0].message.content.strip()
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(result_text)

        if result.get("amount") is None:
            return None

        return result

    except Exception as e:
        # Fallback to regex if LLM fails
        amount_match = re.search(r"(\d+(?:\.\d{1,2})?)", text)
        if not amount_match:
            return None

        amount = float(amount_match.group(1))
        text_lower = text.lower()
        category = "Other"
        for keyword, cat in CATEGORY_MAP.items():
            if keyword in text_lower:
                category = cat
                break

        return {
            "amount": amount,
            "category": category,
            "description": text
        }