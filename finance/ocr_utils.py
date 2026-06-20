import pytesseract
from PIL import Image
import io
import re
from .nlp_utils import extract_expense_from_text

# On Windows, set the tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_expense_from_receipt(receipt_file) -> dict:
    """
    Extract expense details from a receipt image using OCR.
    """
    try:
        image = Image.open(receipt_file)

        # Preprocess for better OCR
        image = image.convert("L")  # grayscale

        # Extract text
        text = pytesseract.image_to_string(image)

        # Try to find total amount
        amount = extract_total_from_receipt(text)

        # Use LLM to understand the receipt
        if amount:
            result = {
                "amount": amount,
                "raw_text": text[:500],
                "category": detect_merchant_category(text),
                "description": f"Receipt: {extract_merchant_name(text)}"
            }
        else:
            result = extract_expense_from_text(text)
            if result:
                result["raw_text"] = text[:500]

        return result

    except Exception as e:
        return {"error": str(e), "raw_text": ""}


def extract_total_from_receipt(text: str) -> float:
    """Extract total amount from receipt text."""
    patterns = [
        r"total[:\s]+₹?\s*(\d+(?:\.\d{1,2})?)",
        r"grand total[:\s]+₹?\s*(\d+(?:\.\d{1,2})?)",
        r"amount[:\s]+₹?\s*(\d+(?:\.\d{1,2})?)",
        r"₹\s*(\d+(?:\.\d{1,2})?)",
        r"rs\.?\s*(\d+(?:\.\d{1,2})?)",
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))
    return None


def extract_merchant_name(text: str) -> str:
    """Extract merchant name from first line of receipt."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[0] if lines else "Unknown Merchant"


def detect_merchant_category(text: str) -> str:
    """Detect category based on receipt text."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["restaurant", "cafe", "food", "hotel", "kitchen", "biryani", "pizza"]):
        return "Food & Dining"
    if any(w in text_lower for w in ["pharmacy", "medical", "hospital", "clinic", "drug"]):
        return "Health"
    if any(w in text_lower for w in ["supermarket", "grocery", "mart", "store", "bazaar"]):
        return "Food & Dining"
    if any(w in text_lower for w in ["petrol", "fuel", "gas station"]):
        return "Transport"
    if any(w in text_lower for w in ["amazon", "flipkart", "mall", "shop"]):
        return "Shopping"
    return "Other"