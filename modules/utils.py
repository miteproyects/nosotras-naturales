"""
Utility Functions Module

Common utility functions for the doTERRA Nosotras Naturales Streamlit app.
Includes JSON handling, WhatsApp links, QR codes, formatting, and validation.
"""

import json
import os
import re
import io
import base64
from urllib.parse import quote
from typing import Any, Dict, List, Optional, Tuple
import logging
import qrcode
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# JSON File Operations
# ============================================================================

def load_json(filepath: str) -> Optional[Any]:
    """
    Load JSON data from a file with error handling.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data, or None if file doesn't exist or is invalid
    """
    try:
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Loaded JSON from {filepath}")
            return data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {str(e)}")
        return None


def save_json(filepath: str, data: Any) -> bool:
    """
    Save data to JSON file with pretty formatting and error handling.

    Args:
        filepath: Path to JSON file
        data: Data to save

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved JSON to {filepath}")
            return True

    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {str(e)}")
        return False


# ============================================================================
# WhatsApp Integration
# ============================================================================

def sanitize_phone(phone: str) -> str:
    """
    Clean and validate phone number for WhatsApp.

    Removes spaces, dashes, parentheses and ensures proper format.

    Args:
        phone: Raw phone number string

    Returns:
        Sanitized phone number (e.g., '5910912345678')
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)

    # Remove '+' prefix if present
    cleaned = cleaned.lstrip('+')

    # Remove leading 0 for some countries (optional, depends on use case)
    # For now, keep it as is

    return cleaned


def get_whatsapp_link(phone: str, message: str = "") -> str:
    """
    Generate a WhatsApp message link.

    Creates a WhatsApp Web API link that opens a chat with pre-filled message.

    Args:
        phone: Phone number (with or without country code, e.g., '+5910912345678' or '5910912345678')
        message: Pre-filled message text

    Returns:
        WhatsApp link URL
    """
    phone = sanitize_phone(phone)

    # Encode message for URL
    encoded_message = quote(message)

    # WhatsApp Web API format
    return f"https://wa.me/{phone}?text={encoded_message}"


# ============================================================================
# doTERRA Links
# ============================================================================

def get_doterra_shop_link(country_code: str, referral_id: str) -> str:
    """
    Generate a doTERRA shop link with referral ID.

    Args:
        country_code: Country code (e.g., 'EC', 'CO', 'PE')
        referral_id: Suzanna's referral ID

    Returns:
        Full doTERRA shop URL with referral parameter
    """
    if not country_code or not referral_id:
        return "https://www.doterra.com"

    return f"https://www.doterra.com/{country_code}?referralId={referral_id}"


# ============================================================================
# Formatting Functions
# ============================================================================

def format_price(price: float, currency: str = "USD") -> str:
    """
    Format price with currency symbol.

    Args:
        price: Price amount
        currency: Currency code (default: USD)

    Returns:
        Formatted price string (e.g., '$99.99 USD')
    """
    if currency == "USD":
        return f"${price:.2f} USD"
    elif currency == "EUR":
        return f"€{price:.2f} EUR"
    else:
        return f"{price:.2f} {currency}"


def get_fda_disclaimer() -> str:
    """
    Get the Spanish FDA disclaimer text.

    Returns:
        FDA disclaimer in Spanish
    """
    disclaimer = (
        "**Aviso Legal:** Estas declaraciones no han sido evaluadas por la FDA. "
        "Este producto no está diseñado para diagnosticar, tratar, curar o prevenir ninguna enfermedad. "
        "Los resultados pueden variar. Consulta con un profesional de salud antes de usar, especialmente si estás "
        "embarazada, amamantando, tomando medicamentos o tienes condiciones médicas preexistentes.\n\n"
        "doTERRA es una marca registrada de doTERRA Essential Oils, LLC."
    )
    return disclaimer


def get_product_image_placeholder(product_type: str = "default") -> str:
    """
    Generate an HTML/CSS gradient placeholder for product images.

    Args:
        product_type: Type of product (e.g., 'essential-oil', 'supplement', 'skincare')

    Returns:
        HTML div with styled gradient background
    """
    gradients = {
        "essential-oil": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "supplement": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "skincare": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "diffuser": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "wellness": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "default": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    }

    gradient = gradients.get(product_type, gradients["default"])

    html = f"""
    <div style="
        width: 100%;
        height: 200px;
        background: {gradient};
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        text-align: center;
        padding: 10px;
        box-sizing: border-box;
    ">
        Imagen no disponible
    </div>
    """
    return html


# ============================================================================
# Symptom/Product Matching
# ============================================================================

def calculate_tag_match_score(user_tags: List[str], result_tags: List[str]) -> float:
    """
    Calculate a match score between user tags and result tags.

    Used for symptom checker and product recommendation matching.

    Args:
        user_tags: List of user-provided tags (e.g., ['stress', 'sleep'])
        result_tags: List of result tags (e.g., ['relaxation', 'stress', 'insomnia'])

    Returns:
        Match score between 0.0 and 1.0
    """
    if not user_tags or not result_tags:
        return 0.0

    # Normalize tags
    user_tags = [tag.lower().strip() for tag in user_tags]
    result_tags = [tag.lower().strip() for tag in result_tags]

    # Count exact matches
    matches = sum(1 for tag in user_tags if tag in result_tags)

    # Calculate score
    score = matches / len(user_tags)

    return round(score, 2)


# ============================================================================
# QR Code Generation
# ============================================================================

def generate_qr_code(url: str, size: int = 10, border: int = 2) -> bytes:
    """
    Generate a QR code image as PNG bytes.

    Args:
        url: URL to encode in QR code
        size: Size of QR code modules (default: 10)
        border: Border size in modules (default: 2)

    Returns:
        PNG image as bytes
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return img_byte_arr.getvalue()

    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise


def generate_qr_code_base64(url: str, size: int = 10, border: int = 2) -> str:
    """
    Generate a QR code and return as base64 string.

    Useful for embedding in HTML/markdown.

    Args:
        url: URL to encode
        size: Size of QR code modules
        border: Border size in modules

    Returns:
        Base64 encoded PNG image
    """
    try:
        qr_bytes = generate_qr_code(url, size, border)
        return base64.b64encode(qr_bytes).decode()
    except Exception as e:
        logger.error(f"Error generating QR code base64: {str(e)}")
        raise


# ============================================================================
# Validation Functions
# ============================================================================

def is_valid_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email string to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str, min_length: int = 10, max_length: int = 15) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number string
        min_length: Minimum length (default: 10)
        max_length: Maximum length (default: 15)

    Returns:
        True if valid phone format
    """
    cleaned = sanitize_phone(phone)
    return min_length <= len(cleaned) <= max_length and cleaned.isdigit()


# ============================================================================
# Text Processing
# ============================================================================

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add (default: "...")

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in text with markdown bold.

    Args:
        text: Original text
        keywords: List of keywords to highlight

    Returns:
        Text with highlighted keywords (markdown format)
    """
    result = text
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub(f"**{keyword}**", result)
    return result


# ============================================================================
# Date/Time Utilities
# ============================================================================

def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Format datetime object to string.

    Args:
        dt: Datetime object
        format_str: Format string (default: "dd/mm/yyyy HH:MM")

    Returns:
        Formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt

    return dt.strftime(format_str)


def get_time_ago(dt: datetime) -> str:
    """
    Get human-readable time difference from now.

    Args:
        dt: Datetime object or ISO string

    Returns:
        Human-readable time string (e.g., "2 hours ago")
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return "Hace poco"

    now = datetime.now()
    if dt.tzinfo:
        now = now.replace(tzinfo=dt.tzinfo)

    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Hace unos segundos"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"Hace {hours} hora{'s' if hours > 1 else ''}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"Hace {days} día{'s' if days > 1 else ''}"
    else:
        weeks = int(seconds / 604800)
        return f"Hace {weeks} semana{'s' if weeks > 1 else ''}"


# ============================================================================
# Data Conversion
# ============================================================================

def dict_to_csv(data: List[Dict], filepath: str) -> bool:
    """
    Convert list of dictionaries to CSV file.

    Args:
        data: List of dictionaries
        filepath: Output CSV file path

    Returns:
        True if successful
    """
    try:
        import csv
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if not data:
            return False

        keys = data[0].keys()

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        return True
    except Exception as e:
        logger.error(f"Error converting to CSV: {str(e)}")
        return False


# ============================================================================
# Caching Utilities
# ============================================================================

class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        """Initialize cache."""
        self._cache = {}
        self._timestamps = {}

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """
        Set a cache value with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def get(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        """
        Get a cache value if not expired.

        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds

        Returns:
            Cached value or None if expired/not found
        """
        if key not in self._cache:
            return None

        if key in self._timestamps:
            age = (datetime.now() - self._timestamps[key]).total_seconds()
            if age > ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                return None

        return self._cache[key]

    def clear(self, key: str = None) -> None:
        """
        Clear cache.

        Args:
            key: Specific key to clear (or None to clear all)
        """
        if key:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._timestamps.clear()


# ============================================================================
# Testing/Demo Functions
# ============================================================================

if __name__ == "__main__":
    # Test functions

    # Test JSON operations
    test_data = {"nombre": "Suzanna", "pais": "Ecuador"}
    save_json("test_data.json", test_data)
    loaded = load_json("test_data.json")
    print(f"JSON test: {loaded}")

    # Test WhatsApp link
    whatsapp_link = get_whatsapp_link("+593991234567", "Hola, quisiera saber más")
    print(f"WhatsApp link: {whatsapp_link}")

    # Test doTERRA link
    shop_link = get_doterra_shop_link("EC", "8205768")
    print(f"Shop link: {shop_link}")

    # Test price formatting
    print(f"Price: {format_price(99.99)}")

    # Test QR code
    qr_bytes = generate_qr_code("https://www.doterra.com/EC?referralId=8205768")
    print(f"QR code generated: {len(qr_bytes)} bytes")

    # Test tag matching
    score = calculate_tag_match_score(["stress", "sleep"], ["stress", "relaxation"])
    print(f"Match score: {score}")

    # Test email validation
    print(f"Email valid: {is_valid_email('test@example.com')}")

    # Test phone validation
    print(f"Phone valid: {is_valid_phone('+593991234567')}")

    # Test text truncation
    print(f"Truncated: {truncate_text('Este es un texto muy largo que necesita ser truncado', 30)}")

    # Test time ago
    past = datetime.now()
    print(f"Time ago: {get_time_ago(past)}")
