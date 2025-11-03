import re
import secrets
import string
from typing import Any, Dict, Optional, List
from datetime import datetime, date
from decimal import Decimal
import json
import uuid


def generate_random_string(length: int = 8) -> str:
    """إنشاء سلسلة عشوائية"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_uuid() -> str:
    """إنشاء UUID"""
    return str(uuid.uuid4())


def generate_slug(text: str) -> str:
    """إنشاء slug من النص"""
    # تحويل إلى أحرف صغيرة
    text = text.lower()
    
    # إزالة الأحرف غير المرغوب فيها
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # استبدال المسافات والشرطات المتعددة بشرطة واحدة
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    
    # إزالة الشرطات من البداية والنهاية
    text = text.strip('-')
    
    return text


def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    # التحقق من أرقام الهاتف السعودية (05xxxxxxxx)
    pattern = r'^05[0-9]{8}$'
    return re.match(pattern, phone) is not None


def mask_email(email: str) -> str:
    """إخفاء جزء من البريد الإلكتروني"""
    if '@' not in email:
        return email
    
    username, domain = email.split('@')
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"


def format_phone(phone: str) -> str:
    """تنسيق رقم الهاتف"""
    # إزالة الرموز غير الرقمية
    digits = re.sub(r'\D', '', phone)
    
    # إضافة رمز الدولة السعودي إذا لم يكن موجوداً
    if not digits.startswith('966'):
        if digits.startswith('0'):
            digits = '966' + digits[1:]
        else:
            digits = '966' + digits
    
    return f"+{digits}"


def parse_phone(phone: str) -> str:
    """تحليل رقم الهاتف واستخراج الأرقام فقط"""
    return re.sub(r'\D', '', phone)


def to_dict(obj: Any) -> Dict[str, Any]:
    """تحويل كائن إلى قاموس"""
    if hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, dict):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return str(obj)
    else:
        return str(obj)


def ensure_dict(data: Any) -> Dict[str, Any]:
    """التأكد من أن البيانات هي قاموس"""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
    elif isinstance(data, dict):
        return data
    else:
        return {}


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """الحصول على قيمة بأمان من القاموس"""
    try:
        return data.get(key, default)
    except (AttributeError, TypeError):
        return default


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """تقسيم القائمة إلى مجموعات"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """إزالة القيم الفارغة من القاموس"""
    return {k: v for k, v in data.items() if v is not None and v != ''}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """دمج عدة قواميس"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def capitalize_words(text: str) -> str:
    """تكبير الحرف الأول من كل كلمة"""
    return ' '.join(word.capitalize() for word in text.split())


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """قطع النص إذا كان أطول من الحد المحدد"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_filename(filename: str) -> str:
    """تنظيف اسم الملف"""
    # إزالة الأحرف غير المرغوب فيها
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # استبدال المسافات بشرطات
    filename = re.sub(r'\s+', '-', filename)
    
    # تحويل إلى أحرف صغيرة
    filename = filename.lower()
    
    return filename


def is_valid_uuid(uuid_str: str) -> bool:
    """التحقق من صحة UUID"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def convert_to_camel_case(text: str) -> str:
    """تحويل النص إلى camelCase"""
    words = re.split(r'[\s_-]+', text)
    if not words:
        return ''
    
    first_word = words[0].lower()
    other_words = [word.capitalize() for word in words[1:]]
    
    return first_word + ''.join(other_words)


def convert_to_snake_case(text: str) -> str:
    """تحويل النص إلى snake_case"""
    # إضافة مسافات قبل الأحرف الكبيرة وتحويلها إلى أحرف صغيرة
    text = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
    return text.lower()


def get_client_ip(request) -> str:
    """الحصول على عنوان IP للعميل"""
    # التحقق من headers مختلفة للحصول على IP الحقيقي
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "0.0.0.0"


def format_currency(amount: float, currency: str = "SAR") -> str:
    """تنسيق العملة"""
    if currency == "SAR":
        return f"{amount:,.2f} ريال"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def calculate_percentage(value: float, total: float) -> float:
    """حساب النسبة المئوية"""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


def format_file_size(size_bytes: int) -> str:
    """تنسيق حجم الملف"""
    if size_bytes == 0:
        return "0 Bytes"
    
    size_names = ["Bytes", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
