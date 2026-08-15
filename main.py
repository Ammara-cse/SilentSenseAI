import time
import requests
from arduino.app_utils import Bridge

# --- TELEGRAM CREDENTIALS ---
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TELEGRAM_BOT_TOKEN"

last_motion_state = None
last_panic_state = False
last_alert_time = 0

def send_telegram_alert(message_text):
    """Sends Telegram alert using onboard Wi-Fi interface."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown",
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print("📲 Telegram alert sent successfully!", flush=True)
        else:
            print(f"❌ Telegram alert failed: {response.text}", flush=True)
    except Exception as e:
        print(f"❌ Telegram error: {e}", flush=True)

def main():
    global last_motion_state, last_panic_state, last_alert_time
    
    print("==========================================", flush=True)
    print("📡 SILENTSENSE SYSTEM STARTED", flush=True)
    print("🎧 Monitoring PIR & Panic Button...", flush=True)
    print("==========================================", flush=True)

    while True:
        try:
            motion_detected = bool(Bridge.call("get_motion"))
            panic_pressed = bool(Bridge.call("get_panic"))

            # --- 1. PANIC BUTTON TRIGGER ---
            if panic_pressed and not last_panic_state:
                now_str = time.strftime('%H:%M:%S')
                panic_message = (
                    f"🚨 *EMERGENCY PANIC ALERT!* 🚨\n\n"
                    f"⏰ *Time:* {now_str}\n"
                    f"🆘 *Status:* Panic Button Pressed!\n"
                    f"💡 *Action:* Light / Buzzer Turned ON!"
                )
                print("🆘 PANIC BUTTON PRESSED!", flush=True)
                send_telegram_alert(panic_message)
                last_panic_state = True
            elif not panic_pressed:
                last_panic_state = False

            # --- 2. PIR MOTION SENSOR TRIGGER ---
            if last_motion_state is None:
                last_motion_state = motion_detected

            if motion_detected != last_motion_state:
                if motion_detected:
                    print("🚨 Motion Detected! LED turned OFF.", flush=True)
                else:
                    print("💡 No motion for 30s! LED turned ON.", flush=True)
                    current_time = time.time()
                    
                    if current_time - last_alert_time > 10:
                        now_str = time.strftime('%H:%M:%S')
                        motion_message = (
                            f"🚨 *SILENTSENSE ALERT* 🚨\n\n"
                            f"⏰ *Time:* {now_str}\n"
                            f"💡 *Light Status:* ON (LED Turned ON)\n"
                            f"⚠️ *Motion Status:* No motion for 30s!"
                        )
                        send_telegram_alert(motion_message)
                        last_alert_time = current_time
                        
                last_motion_state = motion_detected

        except Exception as e:
            print(f"⚠️ App error: {e}", flush=True)
            
        time.sleep(0.2)

if __name__ == "__main__":
    main()