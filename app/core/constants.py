# رموز حالة HTTP
HTTP_STATUS = {
    "SUCCESS": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "SERVER_ERROR": 500,
}

# رسائل الأخطاء
ERROR_MESSAGES = {
    "UNAUTHORIZED": "يجب تسجيل الدخول أولاً",
    "FORBIDDEN": "ليس لديك صلاحية للوصول لهذا المورد",
    "NOT_FOUND": "المورد المطلوب غير موجود",
    "VALIDATION_ERROR": "بيانات غير صحيحة",
    "DUPLICATE_ENTRY": "العنصر موجود مسبقاً",
    "SERVER_ERROR": "خطأ في الخادم",
}

# رسائل النجاح
SUCCESS_MESSAGES = {
    "CREATED": "تم الإنشاء بنجاح",
    "UPDATED": "تم التحديث بنجاح",
    "DELETED": "تم الحذف بنجاح",
    "LOGGED_IN": "تم تسجيل الدخول بنجاح",
    "LOGGED_OUT": "تم تسجيل الخروج بنجاح",
    "PASSWORD_CHANGED": "تم تغيير كلمة المرور بنجاح",
    "EMAIL_SENT": "تم إرسال البريد الإلكتروني بنجاح",
}

# أنواع الاشتراكات
SUBSCRIPTION_PLANS = {
    "trial": {
        "name": "تجريبي",
        "price": 0.0,
        "max_users": 5,
        "max_branches": 1,
        "duration_days": 14
    },
    "basic": {
        "name": "أساسي",
        "price": 29.99,
        "max_users": 25,
        "max_branches": 5,
        "duration_days": 30
    },
    "professional": {
        "name": "احترافي",
        "price": 79.99,
        "max_users": 100,
        "max_branches": 20,
        "duration_days": 30
    },
    "enterprise": {
        "name": "مؤسسي",
        "price": 199.99,
        "max_users": -1,  # Unlimited
        "max_branches": -1,  # Unlimited
        "duration_days": 30
    }
}

# أنواع الفروع
BRANCH_TYPES = {
    "headquarters": "المقر الرئيسي",
    "branch": "فرع",
    "office": "مكتب",
    "store": "متجر",
    "warehouse": "مستودع"
}

# أنواع المستخدمين
USER_TYPES = {
    "admin": "مدير",
    "manager": "مدير فرعي",
    "employee": "موظف",
    "viewer": "مشاهد",
    "guest": "ضيف"
}

# أوضاع الفوترة
BILLING_CYCLES = {
    "monthly": {
        "name": "شهري",
        "months": 1
    },
    "quarterly": {
        "name": "ربع سنوي",
        "months": 3
    },
    "yearly": {
        "name": "سنوي",
        "months": 12
    }
}

# إعدادات النظام
SYSTEM_SETTINGS = {
    "DEFAULT_LANGUAGE": "ar",
    "DEFAULT_TIMEZONE": "Asia/Riyadh",
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOCKOUT_DURATION_MINUTES": 30,
    "PASSWORD_MIN_LENGTH": 8,
    "EMAIL_VERIFICATION_REQUIRED": True,
    "TWO_FACTOR_REQUIRED": False,
    "SESSION_TIMEOUT_MINUTES": 60,
    "MAX_FILE_SIZE_MB": 10,
    "ALLOWED_FILE_TYPES": [".pdf", ".doc", ".docx", ".jpg", ".png", ".xlsx", ".csv"]
}

# رموز البريد الإلكتروني
EMAIL_SUBJECTS = {
    "WELCOME": "مرحباً بك في نظام SaaS",
    "EMAIL_VERIFICATION": "تأكيد عنوان البريد الإلكتروني",
    "PASSWORD_RESET": "إعادة تعيين كلمة المرور",
    "ACCOUNT_ACTIVATED": "تم تفعيل حسابك",
    "SUBSCRIPTION_EXPIRING": "انتهاء الاشتراك قريباً",
    "SUBSCRIPTION_EXPIRED": "انتهى الاشتراك"
}

# إعدادات الأمان
SECURITY_SETTINGS = {
    "JWT_SECRET_KEY_LENGTH": 32,
    "ACCESS_TOKEN_EXPIRE_MINUTES": 60,
    "REFRESH_TOKEN_EXPIRE_DAYS": 30,
    "PASSWORD_RESET_TOKEN_EXPIRE_HOURS": 24,
    "EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS": 24,
    "BCRYPT_ROUNDS": 12
}

# أنواع الأنشطة المسجلة
ACTIVITY_TYPES = {
    "LOGIN": "تسجيل دخول",
    "LOGOUT": "تسجيل خروج",
    "CREATE_USER": "إنشاء مستخدم",
    "UPDATE_USER": "تحديث مستخدم",
    "DELETE_USER": "حذف مستخدم",
    "CREATE_TENANT": "إنشاء مستأجر",
    "UPDATE_TENANT": "تحديث مستأجر",
    "DELETE_TENANT": "حذف مستأجر",
    "CREATE_BRANCH": "إنشاء فرع",
    "UPDATE_BRANCH": "تحديث فرع",
    "DELETE_BRANCH": "حذف فرع",
    "LOGIN_FAILED": "فشل تسجيل الدخول",
    "PASSWORD_CHANGED": "تغيير كلمة المرور",
    "EMAIL_VERIFIED": "تأكيد البريد الإلكتروني"
}
