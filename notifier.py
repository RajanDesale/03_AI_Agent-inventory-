"""Message senders. Telegram = free. Fast2SMS = paid (optional)."""
import requests

import config


def send_telegram(text: str) -> bool:
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        print("[telegram] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is empty in .env "
              "(did you save .env and restart the agent?)")
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN.strip()}/sendMessage",
            json={"chat_id": config.TELEGRAM_CHAT_ID.strip(), "text": text},
            timeout=10,
        )
        if not r.ok:
            try:
                desc = r.json().get("description", r.text)
            except ValueError:
                desc = r.text
            print(f"[telegram] failed ({r.status_code}): {desc}")
        return r.ok
    except requests.RequestException as e:
        print(f"[telegram] network error: {e}")
        return False


def send_sms(number: str, text: str) -> bool:
    """Fast2SMS 'quick' route. Check your Fast2SMS dashboard for current pricing/DLT rules."""
    if not (config.FAST2SMS_API_KEY and number):
        return False
    try:
        r = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": config.FAST2SMS_API_KEY},
            json={"route": "q", "message": text, "numbers": number.replace("+91", "").strip()},
            timeout=10,
        )
        return r.ok and r.json().get("return", False)
    except (requests.RequestException, ValueError):
        return False


def alert_owner(text: str) -> list:
    """Send to every enabled owner channel. Always falls back to console."""
    used = []
    if send_telegram(text):
        used.append("telegram")
    if config.OWNER_SMS and send_sms(config.OWNER_PHONE, text):
        used.append("sms")
    if not used:
        print(f"\n[OWNER ALERT - console only, no channel configured]\n{text}\n")
        used.append("console")
    return used


def thank_customer_sms(phone: str, text: str) -> bool:
    return bool(config.CUSTOMER_SMS and phone and send_sms(phone, text))
