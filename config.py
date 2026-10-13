import os
from dotenv import load_dotenv

load_dotenv()

def _bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y")

SHOP_NAME = os.getenv("SHOP_NAME", "My Electronics Shop")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shop.db")
LOW_STOCK_DEFAULT = int(os.getenv("LOW_STOCK_DEFAULT", "5"))
ALERT_ON_EVERY_SALE = _bool("ALERT_ON_EVERY_SALE", "true")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "")
OWNER_PHONE = os.getenv("OWNER_PHONE", "")
OWNER_SMS = _bool("OWNER_SMS")
CUSTOMER_SMS = _bool("CUSTOMER_SMS")
