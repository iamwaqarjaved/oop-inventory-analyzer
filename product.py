"""
inventory_oop/product.py
========================
Core domain model: Product dataclass and PerishableProduct subclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Product:
    """Represents a single SKU in the inventory."""

    name:          str
    sku:           str
    category:      str
    price:         float
    cost:          float
    stock:         int
    reorder_point: int
    last_sold:     str          # ISO-8601 date string, e.g. "2025-03-15"

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def margin(self) -> float:
        """Gross margin as a decimal fraction (0-1)."""
        if self.price == 0:
            return 0.0
        return (self.price - self.cost) / self.price

    @property
    def margin_pct(self) -> float:
        """Gross margin as a percentage (0-100)."""
        return self.margin * 100

    @property
    def is_below_reorder(self) -> bool:
        """True when current stock is at or below the reorder point."""
        return self.stock <= self.reorder_point

    @property
    def retail_value(self) -> float:
        """Total retail value of units on hand."""
        return self.price * self.stock

    @property
    def last_sold_date(self) -> Optional[date]:
        """Parse last_sold string to a date object, or None on bad data."""
        try:
            return date.fromisoformat(self.last_sold)
        except (ValueError, TypeError):
            return None

    @property
    def days_since_last_sale(self) -> int:
        """Days elapsed since the last recorded sale. 9999 if unknown."""
        d = self.last_sold_date
        return (date.today() - d).days if d else 9999

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"Product({self.sku!r}, {self.name!r}, "
            f"stock={self.stock}, margin={self.margin_pct:.1f}%)"
        )


@dataclass
class PerishableProduct(Product):
    """A Product with an expiration date – e.g. food, pharma, cosmetics."""

    expiration_date: str = ""   # ISO-8601 string; default empty for safety

    @property
    def is_expired(self) -> bool:
        """True when the expiration date is in the past."""
        try:
            exp = date.fromisoformat(self.expiration_date)
        except (ValueError, TypeError):
            return False
        return date.today() > exp

    @property
    def days_until_expiry(self) -> int:
        """Positive = days remaining; negative = already expired; 9999 if unknown."""
        try:
            exp = date.fromisoformat(self.expiration_date)
        except (ValueError, TypeError):
            return 9999
        return (exp - date.today()).days

    def __str__(self) -> str:
        tag = " [EXPIRED]" if self.is_expired else f" [exp {self.expiration_date}]"
        return super().__str__().rstrip(")") + tag + ")"
