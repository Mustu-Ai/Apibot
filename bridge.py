import json
import requests

# ----------------------------------------
# إعدادات Telegram
# ----------------------------------------
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
CHANNEL_ID = "@your_channel"  # أو رقم القناة -100xxxxxx

# ----------------------------------------
# دالة الجسر الرئيسية
# ----------------------------------------
def handler(request):
    """
    يتلقى JSON من الوكلاء:
    - type = "publish" → إرسال منشور إلى القناة
    - type = "reply"   → إرسال رسالة رد إلى مستخدم معين
    """
    body = request.json()

    # =======================
    # 1) نشر منشور (Publisher Agent)
    # =======================
    if body.get("type") == "publish":
        text = body.get("text", "")
        photo = body.get("photo", None)

        if photo:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            payload = {"chat_id": CHANNEL_ID, "caption": text, "photo": photo}
            res = requests.post(url, json=payload)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHANNEL_ID, "text": text}
            res = requests.post(url, json=payload)

        return {"status": "published", "telegram_response": res.json()}

    # =======================
    # 2) رد على مستخدم (Analyzer Agent)
    # =======================
    if body.get("type") == "reply":
        text = body.get("text", "")
        user_id = body.get("user_id")
        if not user_id:
            return {"error": "user_id required for reply"}

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": user_id, "text": text}
        res = requests.post(url, json=payload)

        return {"status": "replied", "telegram_response": res.json()}

    return {"error": "Invalid request format"}
