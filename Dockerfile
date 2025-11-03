FROM python:3.11-slim

# إعداد متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# إعداد مسار العمل
WORKDIR /app

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY . .

# إنشاء مستخدم غير root
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# فتح منفذ التطبيق
EXPOSE 8000

# أمر بدء التشغيل
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]