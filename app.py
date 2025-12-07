import os
import requests
from flask import Flask, request, jsonify

# --- إعداد المتغيرات ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

app = Flask(__name__)


# -----------------------------------------------------
# 🎯 نقطة نهاية التوجيه العامة
# -----------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "endpoints": ["/publish", "/route_telegram/<method>"]
    })
@app.route("/route_telegram/<method_name>", methods=["GET", "POST"])
def route_telegram(method_name):

    if not BOT_TOKEN:
        return jsonify({
            "ok": False,
            "error_code": 500,
            "description": "BOT_TOKEN is not configured"
        }), 500

    url = TELEGRAM_API_BASE_URL + method_name

    # البيانات
    data = request.form.to_dict() if request.form else (
        request.get_json(silent=True) or {})

    # الملفات (Telegram يريدها بهذه الصيغة)
    files = {}
    for key, file_storage in request.files.items():
        files[key] = (
            file_storage.filename,
            file_storage.read(),  # مهم جدًا!
            file_storage.content_type)

    try:
        response = requests.post(url, data=data, files=files, timeout=15)
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({
            "ok":
            False,
            "description":
            f"Error contacting Telegram API: {str(e)}"
        }), 500


# -----------------------------------------------------
# 🚀 نقطة نهاية مخصصة للنشر
# -----------------------------------------------------
@app.route("/publish", methods=["POST"])
def handle_publish_request():

    image_file = request.files.get('image')

    method = "sendPhoto" if image_file else "sendMessage"
    return route_telegram(method)


# -----------------------------------------------------
# ⚙️ تشغيل التطبيق على Replit
# -----------------------------------------------------
if __name__ == "__main__":
    # Replit يجب أن يستخدم البورت 8080 فقط
    port = 8080
   #app.run(host="0.0.0.0", port=port)
