import os
import requests
import json
from base64 import b64decode
from typing import Dict, Any, Optional

# --- الإعدادات ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

if not BOT_TOKEN:
    print("⚠️ Warning: BOT_TOKEN is not set")

# -----------------------------------------
# دالة معالج Netlify الرئيسية (تعادل دالة Lambda)
# -----------------------------------------

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    تعالج طلب HTTP الوارد من Netlify وتوجهه إلى Telegram API.
    """
    if not BOT_TOKEN:
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": "BOT_TOKEN missing"}),
            "headers": {"Content-Type": "application/json"}
        }
    
    # استخراج طريقة Telegram (مثل getChat أو sendMessage)
    path = event.get('path', '/')
    try:
        # تفترض Netlify Functions أن المسار هو: /.netlify/functions/route_telegram/METHOD
        # نحن نبحث عن آخر جزء في المسار.
        method = path.split('/')[-1]
        if not method or method in ("route_telegram", "functions"):
             return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "running",
                    "service": "Telegram Proxy Bridge",
                    "endpoint_example": path + "/getChat"
                }),
                "headers": {"Content-Type": "application/json"}
            }
    except Exception:
        method = ""

    url = TELEGRAM_API_BASE_URL + method
    
    # 1. استخراج البيانات (Body)
    data: Dict[str, Any] = {}
    is_base64_encoded = event.get('isBase64Encoded', False)
    
    body = event.get('body')
    if body:
        if is_base64_encoded:
            body = b64decode(body).decode('utf-8', errors='ignore')
        
        try:
            # محاولة قراءة JSON
            if event.get('headers', {}).get('content-type', '').startswith('application/json'):
                 data = json.loads(body)
            # التعامل مع بيانات الفورم (مثل x-www-form-urlencoded)
            # ملاحظة: Netlify Functions تتعامل مع ملفات/فورم أصعب من Flask
            # لذلك سنركز على JSON للطلبات القادمة من وكيل التحليل.
            # (وكيل التحليل يرسل requests.post(url, json=data))
            else:
                data = json.loads(body) # إذا كان JSON غير محدد
        except json.JSONDecodeError:
            print("Failed to decode body as JSON.")
            # هنا يمكنك إضافة logic لفك تشفير بيانات الفورم يدوياً إذا لزم الأمر
            
    
    # 2. إرسال الطلب إلى Telegram
    try:
        # نستخدم دالة requests.post القياسية
        response = requests.post(url, json=data, timeout=20)
        
        # إعادة الرد إلى وكيل التحليل
        return {
            "statusCode": response.status_code,
            "body": response.text,
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        error_message = str(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": error_message}),
            "headers": {"Content-Type": "application/json"}
        }

# --- ملاحظة حول نقطة النشر الخاصة (/publish) ---
# نقطة /publish غير مدعومة مباشرة هنا.
# يجب أن يستخدم وكيل التحليل دائمًا المسار:
# /route_telegram/sendMessage
# /route_telegram/sendPhoto
# والبيانات تكون في الـ JSON Body.
# النشر المباشر للملفات مع Netlify Functions يتطلب إعداداً أكثر تعقيداً.
# ولأن وكيل التحليل يستخدم فقط getChat/getChatAdministrators، فالتركيز على JSON كافٍ.
