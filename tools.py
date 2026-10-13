"""Functions the Qwen model can call. Alerts + thank-you are done HERE in code,
so they happen every time even if the model forgets."""
import config
import db
import notifier


def get_component_details(query: str) -> dict:
    """Look up component(s) by part number or name and return details, price and stock.

    Args:
        query: Part number (e.g. "LM358") or component name/keywords (e.g. "10k resistor").
    """
    matches = db.find_components(query)
    if not matches:
        return {"found": False, "message": f"No component matching '{query}' in inventory."}
    return {"found": True, "count": len(matches), "components": matches}


def sell_component(part_number: str, quantity: int,
                   customer_name: str = "", customer_phone: str = "") -> dict:
    """Record a sale: reduces stock, alerts the shop owner and thanks the customer.
    Only call when the part number is exact and the quantity is known.

    Args:
        part_number: Exact part number of the component sold.
        quantity: Number of units sold.
        customer_name: Customer name (optional).
        customer_phone: Customer 10-digit mobile number (optional).
    """
    res = db.record_sale(part_number, quantity, customer_name, customer_phone)
    if not res["ok"]:
        return res

    who = customer_name.strip() or "Customer"
    thank_you = (f"Thank you {who} for shopping at {config.SHOP_NAME}! "
                 f"You bought {res['quantity']} x {res['name']} ({res['part_number']}) "
                 f"- total Rs {res['total_inr']}. Visit again!")
    res["thank_you"] = thank_you  # printed by agent.py on the customer side
    notifier.thank_customer_sms(customer_phone, thank_you)

    if config.ALERT_ON_EVERY_SALE or res["is_low"]:
        flag = "LOW STOCK! " if res["is_low"] else ""
        alert = (f"[{config.SHOP_NAME}] {flag}Sold {res['quantity']} x {res['part_number']} "
                 f"({res['name']}). Stock remaining: {res['stock_remaining']}"
                 f" (alert level {res['low_stock_threshold']}).")
        channels = notifier.alert_owner(alert)
        delivered = [c for c in channels if c != "console"]
        res["owner_alert_delivered"] = bool(delivered)
        res["owner_alert_via"] = delivered or ["NONE - Telegram/SMS failed, see terminal"]
    return res


def restock_component(part_number: str, quantity: int) -> dict:
    """Add newly purchased units to stock (owner use).

    Args:
        part_number: Exact part number.
        quantity: Units added.
    """
    return db.add_stock(part_number, quantity)


def list_low_stock() -> dict:
    """List all components at or below their low-stock alert level."""
    items = db.low_stock_items()
    return {"count": len(items), "components": items}


TOOLS = {f.__name__: f for f in
         (get_component_details, sell_component, restock_component, list_low_stock)}
