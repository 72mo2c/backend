import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """التحقق من الحقول المطلوبة"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return missing_fields


def validate_email(email: str) -> Dict[str, Any]:
    """التحقق من صحة البريد الإلكتروني"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not email:
        result["error"] = "البريد الإلكتروني مطلوب"
        return result
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        result["error"] = "صيغة البريد الإلكتروني غير صحيحة"
        return result
    
    result["valid"] = True
    return result


def validate_phone(phone: str) -> Dict[str, Any]:
    """التحقق من صحة رقم الهاتف"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not phone:
        result["error"] = "رقم الهاتف مطلوب"
        return result
    
    # إزالة الرموز غير الرقمية للمقارنة
    digits_only = re.sub(r'\D', '', phone)
    
    # التحقق من رقم سعودي (10 أرقام يبدأ بـ 5)
    if len(digits_only) == 10 and digits_only.startswith('5'):
        result["valid"] = True
        return result
    
    # التحقق من رقم دولي يبدأ بـ 966
    if len(digits_only) == 12 and digits_only.startswith('9665'):
        result["valid"] = True
        return result
    
    result["error"] = "رقم الهاتف غير صحيح"
    return result


def validate_password(password: str) -> Dict[str, Any]:
    """التحقق من قوة كلمة المرور"""
    result = {
        "valid": False,
        "errors": [],
        "strength": "weak"
    }
    
    if not password:
        result["errors"].append("كلمة المرور مطلوبة")
        return result
    
    if len(password) < 8:
        result["errors"].append("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
    
    if not re.search(r'[A-Z]', password):
        result["errors"].append("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
    
    if not re.search(r'[a-z]', password):
        result["errors"].append("كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل")
    
    if not re.search(r'\d', password):
        result["errors"].append("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["errors"].append("كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل")
    
    if not result["errors"]:
        result["valid"] = True
        
        # تحديد قوة كلمة المرور
        if len(password) >= 12 and all([
            re.search(r'[A-Z]', password),
            re.search(r'[a-z]', password),
            re.search(r'\d', password),
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        ]):
            result["strength"] = "strong"
        elif len(password) >= 10:
            result["strength"] = "medium"
    
    return result


def validate_username(username: str) -> Dict[str, Any]:
    """التحقق من صحة اسم المستخدم"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not username:
        result["error"] = "اسم المستخدم مطلوب"
        return result
    
    if len(username) < 3:
        result["error"] = "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"
        return result
    
    if len(username) > 50:
        result["error"] = "اسم المستخدم يجب أن يكون 50 حرف كحد أقصى"
        return result
    
    # يسمح بالأحرف والأرقام والشرطات فقط
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        result["error"] = "اسم المستخدم يمكن أن يحتوي على أحرف وأرقام وشرطات فقط"
        return result
    
    result["valid"] = True
    return result


def validate_name(name: str, field_type: str = "name") -> Dict[str, Any]:
    """التحقق من صحة الاسم"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not name:
        result["error"] = f"{field_type} مطلوب"
        return result
    
    if len(name) < 2:
        result["error"] = f"{field_type} يجب أن يكون حرفين على الأقل"
        return result
    
    if len(name) > 50:
        result["error"] = f"{field_type} يجب أن يكون 50 حرف كحد أقصى"
        return result
    
    # يسمح بالأحرف العربية والإنجليزية والمسافات
    if not re.match(r'^[a-zA-Zأ-ي\s]+$', name):
        result["error"] = f"{field_type} يمكن أن يحتوي على أحرف ومسافات فقط"
        return result
    
    result["valid"] = True
    return result


def validate_url(url: str) -> Dict[str, Any]:
    """التحقق من صحة الرابط"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not url:
        result["error"] = "الرابط مطلوب"
        return result
    
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    if not re.match(url_pattern, url):
        result["error"] = "صيغة الرابط غير صحيحة"
        return result
    
    result["valid"] = True
    return result


def validate_slug(slug: str) -> Dict[str, Any]:
    """التحقق من صحة الـ slug"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not slug:
        result["error"] = "الـ slug مطلوب"
        return result
    
    if len(slug) < 3:
        result["error"] = "الـ slug يجب أن يكون 3 أحرف على الأقل"
        return result
    
    if len(slug) > 100:
        result["error"] = "الـ slug يجب أن يكون 100 حرف كحد أقصى"
        return result
    
    # يسمح بالأحرف الصغيرة والأرقام والشرطات فقط
    if not re.match(r'^[a-z0-9-]+$', slug):
        result["error"] = "الـ slug يمكن أن يحتوي على أحرف صغيرة وأرقام وشرطات فقط"
        return result
    
    # التحقق من عدم البدء أو الانتهاء بشرطة
    if slug.startswith('-') or slug.endswith('-'):
        result["error"] = "الـ slug لا يمكن أن يبدأ أو ينتهي بشرطة"
        return result
    
    result["valid"] = True
    return result


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> Dict[str, Any]:
    """التحقق من صحة التاريخ"""
    result = {
        "valid": False,
        "error": None,
        "date": None
    }
    
    if not date_str:
        result["error"] = "التاريخ مطلوب"
        return result
    
    try:
        parsed_date = datetime.strptime(date_str, format).date()
        result["valid"] = True
        result["date"] = parsed_date
    except ValueError:
        result["error"] = f"صيغة التاريخ غير صحيحة، يجب أن تكون {format}"
    
    return result


def validate_number(value: Union[str, int, float], 
                   min_val: Optional[float] = None, 
                   max_val: Optional[float] = None,
                   field_name: str = "القيمة") -> Dict[str, Any]:
    """التحقق من صحة الرقم"""
    result = {
        "valid": False,
        "error": None,
        "number": None
    }
    
    if value is None or value == '':
        result["error"] = f"{field_name} مطلوبة"
        return result
    
    try:
        number = float(value)
        result["number"] = number
        
        if min_val is not None and number < min_val:
            result["error"] = f"{field_name} يجب أن تكون أكبر من أو تساوي {min_val}"
            return result
        
        if max_val is not None and number > max_val:
            result["error"] = f"{field_name} يجب أن تكون أقل من أو تساوي {max_val}"
            return result
        
        result["valid"] = True
    except (ValueError, TypeError):
        result["error"] = f"{field_name} يجب أن تكون رقماً صحيحاً"
    
    return result


def validate_choice(value: str, choices: List[str], field_name: str = "القيمة") -> Dict[str, Any]:
    """التحقق من صحة الخيار المحدد"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not value:
        result["error"] = f"{field_name} مطلوبة"
        return result
    
    if value not in choices:
        result["error"] = f"{field_name} يجب أن تكون واحدة من: {', '.join(choices)}"
        return result
    
    result["valid"] = True
    return result


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Dict[str, Any]:
    """التحقق من امتداد الملف"""
    result = {
        "valid": False,
        "error": None
    }
    
    if not filename:
        result["error"] = "اسم الملف مطلوب"
        return result
    
    if '.' not in filename:
        result["error"] = "يجب أن يحتوي الملف على امتداد"
        return result
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in [ext.lower().lstrip('.') for ext in allowed_extensions]:
        result["error"] = f"نوع الملف غير مسموح. الأنواع المسموحة: {', '.join(allowed_extensions)}"
        return result
    
    result["valid"] = True
    return result


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """تنظيف النص من الأحرف الضارة"""
    if not text:
        return ""
    
    # إزالة HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # إزالة الأحرف الضارة
    text = re.sub(r'[<>"\']', '', text)
    
    # تقصير النص إذا لزم الأمر
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def validate_data_types(data: Dict[str, Any], schema: Dict[str, str]) -> List[str]:
    """التحقق من أنواع البيانات"""
    errors = []
    
    for field, expected_type in schema.items():
        if field not in data:
            continue
            
        value = data[field]
        
        if value is None:
            continue
            
        try:
            if expected_type == "str" and not isinstance(value, str):
                errors.append(f"{field} يجب أن يكون نصاً")
            elif expected_type == "int" and not isinstance(value, int):
                errors.append(f"{field} يجب أن يكون رقماً صحيحاً")
            elif expected_type == "float" and not isinstance(value, (int, float)):
                errors.append(f"{field} يجب أن يكون رقماً")
            elif expected_type == "bool" and not isinstance(value, bool):
                errors.append(f"{field} يجب أن يكون true أو false")
            elif expected_type == "list" and not isinstance(value, list):
                errors.append(f"{field} يجب أن يكون قائمة")
            elif expected_type == "dict" and not isinstance(value, dict):
                errors.append(f"{field} يجب أن يكون قاموساً")
        except Exception:
            errors.append(f"{field} نوع البيانات غير صالح")
    
    return errors
