import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔑 Telegram Credentials (Yahan apne Details Daalein)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"


def send_emergency_alert(prediction, duration, reasons):
    """Sends immediate alert to phone when risk score is Critical"""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ Telegram token not configured yet.")
        return

    message = (
        f"🚨 *SILENTSENSE AI EMERGENCY ALERT* 🚨\n\n"
        f"⚠️ *Status:* {prediction}\n"
        f"⏱️ *Duration:* {duration} Minutes\n"
        f"📌 *Detected Reasons:*\n"
    )
    for r in reasons:
        message += f"• {r}\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    try:
        requests.post(url, json=payload, timeout=5)
        print("📲 Emergency alert sent to Telegram successfully!")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")


# --- SCIENTIFIC HUMAN PRESENCE ENGINE ---
def analyze_human_state(duration_mins, sensor_signal, light_on, is_night):
    risk_score = 5
    reasons = []

    if sensor_signal == "macro":
        risk_score = 5
        reasons.append("Body movement detected (Active Person)")
        state_label = "Active & Moving"

    elif sensor_signal == "micro":
        risk_score = 8
        reasons.append(
            "Micro-pulses detected (Breathing & subtle chest movements)"
        )
        reasons.append("Biological baseline confirmed: Normal Safe Rest")
        state_label = "Normal Sleeping State"

    elif sensor_signal == "none":
        state_label = "Possible Unresponsive Collapse"
        if duration_mins > 30:
            risk_score += 65
            reasons.append(
                f"Total absence of movement & micro-pulses for {duration_mins} mins"
            )
        else:
            risk_score += 45
            reasons.append(
                f"Sudden loss of human activity for {duration_mins} mins"
            )

        if light_on:
            risk_score += 20
            reasons.append("Room lights remain ON with zero response")

    risk_score = min(max(risk_score, 5), 99)

    if risk_score > 75:
        prediction = (
            "CRITICAL: Unresponsive Person / Silent Emergency Alert"
        )
        # TRIGGER REAL-TIME TELEGRAM ALERT
        send_emergency_alert(prediction, duration_mins, reasons)
    elif risk_score > 35:
        prediction = "WARNING: Prolonged Absence of Human Activity"
    else:
        prediction = "NORMAL: Healthy Human Activity / Safe Rest Pattern"

    return {
        "risk_score": risk_score,
        "prediction": prediction,
        "state_label": state_label,
        "reasons": reasons,
        "duration": duration_mins,
        "sensor_telemetry": "Zero Motion & Zero Micro-Pulses"
        if sensor_signal == "none"
        else "Active Pulses",
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    duration = int(data.get("duration", 45))
    sensor_signal = str(data.get("sensor_signal", "none"))
    light = bool(data.get("light", True))
    is_night = bool(data.get("is_night", False))

    result = analyze_human_state(duration, sensor_signal, light, is_night)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)