"""Run: python test_telegram.py   -> tells you exactly why Telegram alerts fail."""
import os
import config
import notifier

print("Running from folder:", os.getcwd())
print(".env found here:", os.path.exists(".env"))
tok, cid = config.TELEGRAM_BOT_TOKEN.strip(), config.TELEGRAM_CHAT_ID.strip()
print("Token loaded:", "yes" if tok else "NO (empty)")
print("Chat ID loaded:", cid if cid else "NO (empty)")
if tok and ":" in tok:
    print("Token length after colon:", len(tok.split(":", 1)[1]), "(should be 35)")
ok = notifier.send_telegram(f"{config.SHOP_NAME}: test message OK")
print("RESULT:", "SENT - check Telegram" if ok else "FAILED - see reason above")
