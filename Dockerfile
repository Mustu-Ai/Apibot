# استخدام صورة بايثون أساسية مستقرة
FROM python:3.10-slim

# إعداد المتغيرات البيئية الافتراضية
ENV PORT 8080
ENV PYTHONUNBUFFERED 1

# تثبيت gunicorn ومتطلبات النظام الأساسية (إذا لزم الأمر)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ التبعيات وتثبيتها أولاً (لتحسين التخزين المؤقت)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملف الكود الرئيسي
COPY app.py .

# أمر التشغيل: استخدام gunicorn كخادم إنتاج
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT}", "app:app"]
