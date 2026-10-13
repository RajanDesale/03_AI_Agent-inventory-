"""Database layer. All stock changes happen HERE, in plain Python - never by the LLM."""
from datetime import datetime

from sqlalchemy import (Column, DateTime, Float, Integer, String, Text,
                        create_engine, func, or_, select)
from sqlalchemy.orm import declarative_base, sessionmaker

import config

engine = create_engine(config.DATABASE_URL, future=True, pool_pre_ping=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True)
    part_number = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(80))
    manufacturer = Column(String(80))
    description = Column(Text)
    price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=config.LOW_STOCK_DEFAULT)
    location = Column(String(50))  # shelf / bin

    def to_dict(self):
        return {
            "part_number": self.part_number,
            "name": self.name,
            "category": self.category,
            "manufacturer": self.manufacturer,
            "description": self.description,
            "price_inr": self.price,
            "stock": self.stock,
            "low_stock_threshold": self.low_stock_threshold,
            "location": self.location,
        }


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    part_number = Column(String(64), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)


def init_db():
    Base.metadata.create_all(engine)


def find_components(query: str, limit: int = 5):
    """Exact part-number match first, then every word of the query must match
    part number / name / category / manufacturer / description."""
    q = (query or "").strip()
    if not q:
        return []
    with Session() as s:
        exact = s.scalars(
            select(Component).where(func.lower(Component.part_number) == q.lower())
        ).first()
        if exact:
            return [exact.to_dict()]
        stmt = select(Component)
        for word in q.split():
            like = f"%{word.lower()}%"
            stmt = stmt.where(or_(
                func.lower(Component.part_number).like(like),
                func.lower(Component.name).like(like),
                func.lower(func.coalesce(Component.category, "")).like(like),
                func.lower(func.coalesce(Component.manufacturer, "")).like(like),
                func.lower(func.coalesce(Component.description, "")).like(like),
            ))
        return [c.to_dict() for c in s.scalars(stmt.limit(limit)).all()]


def record_sale(part_number, quantity, customer_name="", customer_phone=""):
    """Atomically reduce stock and log the sale."""
    if quantity is None or int(quantity) <= 0:
        return {"ok": False, "error": "Quantity must be a positive number."}
    quantity = int(quantity)
    with Session() as s, s.begin():
        comp = s.scalars(
            select(Component)
            .where(func.lower(Component.part_number) == part_number.strip().lower())
            .with_for_update()
        ).first()
        if not comp:
            return {"ok": False, "error": f"Part number '{part_number}' not found."}
        if comp.stock < quantity:
            return {"ok": False,
                    "error": f"Not enough stock. Only {comp.stock} of {comp.part_number} available."}
        comp.stock -= quantity
        total = round(comp.price * quantity, 2)
        s.add(Sale(part_number=comp.part_number, quantity=quantity, total_price=total,
                   customer_name=customer_name or None, customer_phone=customer_phone or None))
        return {
            "ok": True,
            "part_number": comp.part_number,
            "name": comp.name,
            "quantity": quantity,
            "unit_price_inr": comp.price,
            "total_inr": total,
            "stock_remaining": comp.stock,
            "low_stock_threshold": comp.low_stock_threshold,
            "is_low": comp.stock <= comp.low_stock_threshold,
        }


def add_stock(part_number, quantity):
    if quantity is None or int(quantity) <= 0:
        return {"ok": False, "error": "Quantity must be a positive number."}
    with Session() as s, s.begin():
        comp = s.scalars(
            select(Component)
            .where(func.lower(Component.part_number) == part_number.strip().lower())
            .with_for_update()
        ).first()
        if not comp:
            return {"ok": False, "error": f"Part number '{part_number}' not found."}
        comp.stock += int(quantity)
        return {"ok": True, "part_number": comp.part_number, "name": comp.name,
                "stock_now": comp.stock}


def low_stock_items():
    with Session() as s:
        rows = s.scalars(
            select(Component).where(Component.stock <= Component.low_stock_threshold)
            .order_by(Component.stock)
        ).all()
        return [c.to_dict() for c in rows]
