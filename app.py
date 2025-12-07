import os
import requests
from flask import Flask, request, jsonify

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("⚠️ Warning: BOT_TOKEN is not set")

TELEGRAM_API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

app = Flask(__name__)


# -----------------------------------------
# الصفحة الرئيسية
# -----------------------------------------
@app.route("/")
def home():
    return {
        "status": "running",
        "service": "Telegram Proxy Bridge",
        "endpoints": ["/publish", "/route/<method>"]
    }


# -----------------------------------------
# جسر عام لجميع أوامر Telegram API
# -----------------------------------------
@app.route("/route/<method>", methods=["GET", "POST"])
def route(method):

    if not BOT_TOKEN:
        return jsonify({"ok": False, "error": "BOT_TOKEN missing"}), 500

    url = TELEGRAM_API_BASE_URL + method

    # قراءة البيانات
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    # قراءة الملفات
    files = {}
    for key, file_storage in request.files.items():
        files[key] = (
            file_storage.filename,
            file_storage.read(),
            file_storage.content_type
        )

    try:
        response = requests.post(url, data=data, files=files, timeout=20)
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# -----------------------------------------
# نقطة نشر خاصة
# -----------------------------------------
@app.route("/publish", methods=["POST"])
def publish():
    image_file = request.files.get("image")
    method = "sendPhoto" if image_file else "sendMessage"
    return route(method)


# -----------------------------------------
# تشغيل التطبيق
# -----------------------------------------
if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting server on port {port}")
    serve(app, host="0.0.0.0", port=port)         }), 500

    url = TELEGRAM_API_BASE_URL + method

    # قراءة البيانات
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    # قراءة الملفات (Telegram يريدهم multipart/form-data)
    files = {}
    for key, file_storage in request.files.items():
        files[key] = (
            file_storage.filename,
            file_storage.stream.read(),
            file_storage.content_type
        )

    try:
        resp = requests.post(url, data=data, files=files, timeout=20)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# -----------------------------------------
# مسار خاص بالنشر من HF
# -----------------------------------------
@app.route("/publish", methods=["POST"])
def publish():

    image_file = request.files.get("image")
    method = "sendPhoto" if image_file else "sendMessage"

    return route(method)


# -----------------------------------------
# التشغيل المحلي / Koyeb
# -----------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Running on port {port}")
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)    # الملفات (Telegram يريدها بهذه الصيغة)
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
    app.run(host="0.0.0.0", port=port)
