import os
import requests
from flask import Flask, request, jsonify

# --- إعداد المتغيرات ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

app = Flask(__name__)

# -----------------------------------------------------
# 🎯 نقطة نهاية التوجيه العامة (للإحصائيات والوظائف الأخرى)
# -----------------------------------------------------
@app.route("/route_telegram/<method_name>", methods=["GET", "POST"])
def route_telegram(method_name):
    """
    تقوم هذه النقطة بتمرير أي طلب مباشرة إلى Telegram Bot API.
    (تستخدم لمهام مثل getChatMembersCount للإحصائيات).
    """
    
    # التحقق من توفر مفتاح البوت
    if not BOT_TOKEN:
        return jsonify({"ok": False, "error_code": 500, "description": "BOT_TOKEN is not configured"}), 500

    # بناء رابط Telegram API كاملاً
    url = TELEGRAM_API_BASE_URL + method_name
    
    # 1. جمع البيانات (Form data/JSON)
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    
    # 2. جمع الملفات (إذا وجدت)
    files = {}
    for key, file_storage in request.files.items():
        # يجب أن يكون القيمة tuple (filename, file_object, mimetype)
        files[key] = (file_storage.filename, file_storage.stream, file_storage.content_type)
        
    try:
        # إرسال الطلب إلى Telegram API
        response = requests.post(url, data=data, files=files)
        response.raise_for_status() # إلقاء استثناء لأكواد الحالة 4xx/5xx
        
        # تمرير الرد كما هو إلى مساحة التحليل/النشر
        return jsonify(response.json()), response.status_code

    except requests.exceptions.HTTPError as e:
        # تمرير رسالة الخطأ من Telegram إلى المساحة الطالبة
        error_response = e.response.json()
        return jsonify(error_response), e.response.status_code
        
    except Exception as e:
        return jsonify({"ok": False, "description": f"Internal routing error: {str(e)}"}), 500

# -----------------------------------------------------
# 🚀 نقطة نهاية مخصصة للنشر (لتسهيل رفع الصور)
# -----------------------------------------------------
@app.route("/publish", methods=["POST"])
def handle_publish_request():
    """
    نقطة نهاية مخصصة لاستقبال طلبات النشر مع الصور وتمريرها إلى Telegram.
    (تستخدم method_name = 'sendPhoto' أو 'sendMessage')
    """
    
    image_file = request.files.get('image')
    
    # تحديد method_name: sendPhoto إذا وجدت صورة، و sendMessage للنص فقط
    if image_file:
        method = "sendPhoto"
    else:
        method = "sendMessage"
        
    # إعادة توجيه الطلب إلى نقطة النهاية العامة /route_telegram
    # يتم ذلك عبر استدعاء الدالة مباشرةً، حيث ستقوم بالتعامل مع البيانات والملفات
    return route_telegram(method)


# -----------------------------------------------------
# ⚙️ تشغيل التطبيق (لـ Render)
# -----------------------------------------------------
if __name__ == "__main__":
    # Render يستخدم متغير البيئة PORT لتحديد المنفذ
    port = int(os.environ.get("PORT", 5000))
    # عند استخدام gunicorn (الموصى به لـ Render): gunicorn app:app
    # عند التشغيل المحلي أو باستخدام Start Command: python app.py
    app.run(host="0.0.0.0", port=port)
    
