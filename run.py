#!/usr/bin/env python3
"""
ملف تشغيل سريع للنظام
"""
import os
import sys

# إضافة مسار التطبيق
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

if __name__ == "__main__":
    try:
        import uvicorn
        print("🚀 تشغيل نظام SaaS Backend...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except ImportError:
        print("❌ uvicorn غير مثبت!")
        print("قم بتشغيل: pip install uvicorn[standard]")
        sys.exit(1)