"""Electronics shop AI agent - runs fully local with Ollama (Qwen)."""
import json

import ollama

import config
import db
from tools import TOOLS

SYSTEM_PROMPT = f"""You are the inventory assistant of "{config.SHOP_NAME}", an electronics components shop.
Talk to the shop owner/staff. Be short and clear.

Rules:
1. For ANY question about a part, price, stock or specs, call get_component_details. Never guess or invent specs, prices or stock.
2. If several parts match, list them and ask which one. Do not sell until the part number is exact.
3. To sell, you need exact part number and quantity. Then call sell_component. Stock update, owner alert and customer thank-you are sent automatically by the system - never claim you sent them yourself. Only say the owner was alerted if owner_alert_delivered is true; if false, say the alert FAILED.
4. If the tool says not found or not enough stock, tell that plainly.
5. Prices are in Indian Rupees (Rs).
"""


def run_tool(name, args):
    fn = TOOLS.get(name)
    if not fn:
        return {"ok": False, "error": f"Unknown tool {name}"}
    try:
        return fn(**args)
    except TypeError as e:
        return {"ok": False, "error": f"Bad arguments: {e}"}
    except Exception as e:  # keep the chat alive
        return {"ok": False, "error": str(e)}


def chat_turn(messages):
    for _ in range(6):  # max tool rounds per user message
        resp = ollama.chat(model=config.OLLAMA_MODEL, messages=messages,
                           tools=list(TOOLS.values()))
        msg = resp.message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for call in msg.tool_calls:
            name, args = call.function.name, dict(call.function.arguments)
            result = run_tool(name, args)
            if isinstance(result, dict) and result.get("thank_you"):
                print(f"\n  >>> CUSTOMER MESSAGE: {result['thank_you']}")
                if "owner_alert_delivered" in result:
                    if result["owner_alert_delivered"]:
                        print(f"  >>> OWNER ALERT delivered via: {', '.join(result['owner_alert_via'])}\n")
                    else:
                        print("  >>> OWNER ALERT NOT DELIVERED - fix Telegram (run: python test_telegram.py)\n")
                else:
                    print()
            messages.append({"role": "tool", "tool_name": name,
                             "content": json.dumps(result, default=str)})
    return "Sorry, I couldn't finish that. Please rephrase."


def main():
    db.init_db()
    print(f"{config.SHOP_NAME} agent | model: {config.OLLAMA_MODEL} | type 'exit' to quit")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in ("exit", "quit"):
            break
        if not user:
            continue
        messages.append({"role": "user", "content": user})
        try:
            print("Agent:", chat_turn(messages))
        except Exception as e:
            print(f"[error] {e}\nIs Ollama running and is the model name in .env correct?")
        if len(messages) > 30:  # keep context small for local models
            messages = messages[:1] + messages[-20:]


if __name__ == "__main__":
    main()
