# Electronics Shop AI Agent (Ollama + Qwen, fully local)

Ask for any part by number or name, sell parts by chat, stock updates automatically,
owner gets a stock alert, customer sees a thank-you message.

## Run in VS Code (Windows)
1. Unzip, then File > Open Folder > `electro_shop_agent`.
2. Terminal (Ctrl+`):
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
3. Check your Qwen model name: `ollama list`  -> put it in `.env` as `OLLAMA_MODEL=` (e.g. `qwen2.5:7b`).
   Tool calling needs a Qwen2.5 / Qwen3 model. If missing: `ollama pull qwen2.5:7b`
4. Load sample parts (or your own CSV): `python seed.py`  /  `python seed.py parts.csv`
5. Start: `python agent.py`

## Try
- `details of LM358`
- `10k resistor kitna stock hai?`
- `sell 3 NE555 to Amit, 9876543210`
- `which items are low on stock?`
- `add 50 units of 1N4007`

## Free owner alerts with Telegram
1. Telegram > search @BotFather > /newbot > copy the token into `TELEGRAM_BOT_TOKEN`. #chat-id 8068652088
2. Open your new bot, press Start, send "hi"."""token url---https://api.telegram.org/bot8376949065:AAHw2WZGWjVz5ydkKEevgXZssmQ5yHW0UBo/getUpdates"""
3. Open `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser; copy `"chat":{"id": ...}` into `TELEGRAM_CHAT_ID`.

## Use MySQL instead of SQLite
`pip install PyMySQL`, create database `electro_shop`, set `DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/electro_shop` in `.env`.
