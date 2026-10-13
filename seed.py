"""Load sample parts, or your own CSV:  python seed.py parts.csv
CSV columns: part_number,name,category,manufacturer,description,price,stock,low_stock_threshold,location
"""
import csv
import sys

import db

SAMPLE = [
    ("LM358", "Dual Op-Amp IC", "IC", "Texas Instruments", "Dual low-power op-amp, 3-32V supply, DIP-8", 12, 40, 10, "A1"),
    ("NE555", "555 Timer IC", "IC", "Texas Instruments", "Precision timer, 4.5-16V, DIP-8", 10, 60, 10, "A2"),
    ("ATMEGA328P-PU", "ATmega328P Microcontroller", "Microcontroller", "Microchip", "8-bit AVR, 32KB flash, 2KB SRAM, 20MHz, DIP-28", 220, 15, 5, "B1"),
    ("1N4007", "Rectifier Diode", "Diode", "Generic", "1A, 1000V general-purpose rectifier diode", 2, 200, 50, "C1"),
    ("BC547", "NPN Transistor", "Transistor", "Fairchild", "NPN, 45V, 100mA, TO-92", 3, 120, 30, "C2"),
    ("RES-10K-0.25W", "10k Ohm Resistor 1/4W", "Resistor", "Generic", "10k ohm, 5% tolerance, 0.25W carbon film", 1, 500, 100, "D1"),
    ("CAP-100UF-25V", "100uF 25V Electrolytic Capacitor", "Capacitor", "Generic", "100uF, 25V, radial electrolytic", 4, 80, 20, "D2"),
]


def main():
    db.init_db()
    rows = []
    if len(sys.argv) > 1:
        with open(sys.argv[1], newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows.append((r["part_number"], r["name"], r.get("category"), r.get("manufacturer"),
                             r.get("description"), float(r.get("price") or 0),
                             int(r.get("stock") or 0), int(r.get("low_stock_threshold") or 5),
                             r.get("location")))
    else:
        rows = SAMPLE
    added = 0
    with db.Session() as s, s.begin():
        for pn, name, cat, mfr, desc, price, stock, thr, loc in rows:
            if s.query(db.Component).filter_by(part_number=pn).first():
                continue
            s.add(db.Component(part_number=pn, name=name, category=cat, manufacturer=mfr,
                               description=desc, price=price, stock=stock,
                               low_stock_threshold=thr, location=loc))
            added += 1
    print(f"Added {added} components.")


if __name__ == "__main__":
    main()
