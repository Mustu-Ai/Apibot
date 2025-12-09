import os
import requests
import json
from base64 import b64decode
from typing import Dict, Any, Optional

# --- الإعدادات ---
# يتم جلب BOT_TOKEN من متغيرات البيئة في Netlify
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

if not BOT_TOKEN:
    # طباعة تحذير للسجلات (Logs)
    print("⚠️ Warning: BOT_TOKEN is not set in Netlify environment variables.")

# -----------------------------------------
# دالة معالج Netlify الرئيسية
# -----------------------------------------

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    تعالج طلب HTTP الوارد من Netlify وتوجهه إلى Telegram API.
    """
    
    # 1. التحقق من التهيئات الأساسية (في حال لم يتم تعيين BOT_TOKEN)
    if not BOT_TOKEN:
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": "BOT_TOKEN missing in Netlify environment variables."}),
            "headers": {"Content-Type": "application/json"}
        }

    # 2. تحديد أمر Telegram (Method) من المسار
    path = event.get('path', '/')
    method: str = ""
    
    # محاولة استخلاص أمر Telegram من المسار بعد اسم الوظيفة (route_telegram)
    try:
        # فصل أجزاء المسار
        path_parts = [part for part in path.split('/') if part]
        
        # البحث عن اسم الوظيفة في المسار وأخذ الجزء الذي يليها
        if "route_telegram" in path_parts:
            method_index = path_parts.index("route_telegram") + 1
            if method_index < len(path_parts):
                method = path_parts[method_index]
    except Exception:
        pass

    # 3. التحقق من نوع الطلب والمسار (إرجاع رسالة الترحيب)
    # إذا كان الطلب GET والـ method فارغ (فتح الرابط مباشرة في المتصفح)
    if event.get('httpMethod') == 'GET' and not method:
         # --- رسالة الترحيب المطلوبة ---
         return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "online and ready",
                "service": "Telegram Proxy Bridge (Netlify Function)",
                "message": "👋 أهلاً بك! الجسر يعمل وينتظر طلب POST لـ Telegram API.",
                "endpoint_base": path,
                "example": f"{path}/getChat",
                "note": "لاستخدام الجسر، يجب إرسال طلب HTTP POST إلى الرابط مع إضافة الأمر (مثل: /getChat)."
            }, ensure_ascii=False),
            "headers": {"Content-Type": "application/json"}
        }

    # 4. إذا لم يكن هناك أمر Telegram، أرجع خطأ 400
    if not method:
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Telegram method not provided in URL path."}),
            "headers": {"Content-Type": "application/json"}
        }

    url = TELEGRAM_API_BASE_URL + method
    
    # 5. استخراج البيانات (Body) لطلبات POST
    data: Dict[str, Any] = {}
    
    # فقط نحاول فك التشفير إذا كان هناك محتوى
    if event.get('httpMethod') == 'POST':
        body = event.get('body')
        is_base64_encoded = event.get('isBase64Encoded', False)
        
        if body:
            if is_base64_encoded:
                body = b64decode(body).decode('utf-8', errors='ignore')
            
            try:
                # نفترض أن وكيل التحليل يرسل دائماً JSON
                data = json.loads(body)
            except json.JSONDecodeError:
                print("Failed to decode body as JSON.")
                # إذا فشل JSON، يمكن ترك البيانات فارغة أو التعامل معها كخطأ

    
    # 6. إرسال الطلب إلى Telegram (يحدث فقط إذا كان هناك method)
    try:
        # نستخدم دالة requests.post القياسية
        # الطلبات القادمة من وكيل التحليل ستكون POST
        response = requests.post(url, json=data, timeout=20)
        
        # إعادة الرد إلى وكيل التحليل
        return {
            "statusCode": response.status_code,
            "body": response.text,
            "headers": {"Content-Type": "application/json"}
        }

    except requests.exceptions.Timeout:
         return {
            "statusCode": 504,
            "body": json.dumps({"ok": False, "error": "Telegram API request timed out."}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        error_message = str(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": f"Internal proxy error: {error_message}"}),
            "headers": {"Content-Type": "application/json"}
      }
