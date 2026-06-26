"""
inventory_oop/inventory.py
==========================
Inventory container: holds Products, provides filtering / query methods,
and exposes an alternate constructor Inventory.from_csv(path).
"""

from __future__ import annotations

import csv
from typing import Iterator, Optional

from .product import PerishableProduct, Product


class Inventory:
    """A collection of Products with querying and mutation operations."""

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        self._products: dict[str, Product] = {}   # keyed by SKU

    # ------------------------------------------------------------------
    # Alternate constructor – class-method pattern
    # ------------------------------------------------------------------

    @classmethod
    def from_csv(cls, path: str) -> "Inventory":
        """
        Load inventory from a CSV file and return a populated Inventory.

        Expected columns:
            name, sku, category, price, cost, stock, reorder_point, last_sold
        Optional extra column:
            expiration_date   → row is loaded as PerishableProduct
        """
        inv = cls()
        with open(path, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                common = dict(
                    name          = row["name"],
                    sku           = row["sku"],
                    category      = row["category"],
                    price         = float(row["price"]),
                    cost          = float(row["cost"]),
                    stock         = int(row["stock"]),
                    reorder_point = int(row["reorder_point"]),
                    last_sold     = row.get("last_sold", ""),
                )
                if "expiration_date" in row and row["expiration_date"]:
                    product: Product = PerishableProduct(
                        **common, expiration_date=row["expiration_date"]
                    )
                else:
                    product = Product(**common)
                inv.add(product)
        return inv

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, product: Product) -> None:
        """Add or replace a product (keyed by SKU)."""
        self._products[product.sku] = product

    def remove(self, sku: str) -> Optional[Product]:
        """Remove and return the product with *sku*, or None if not found."""
        return self._products.pop(sku, None)

    # ------------------------------------------------------------------
    # Iteration / access
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[Product]:
        return iter(self._products.values())

    def __len__(self) -> int:
        return len(self._products)

    def get(self, sku: str) -> Optional[Product]:
        """Return the product with *sku*, or None."""
        return self._products.get(sku)

    # ------------------------------------------------------------------
    # Filtering helpers
    # ------------------------------------------------------------------

    def filter_by_category(self, category: str) -> list[Product]:
        """Return all products whose category matches (case-insensitive)."""
        cat = category.lower()
        return [p for p in self if p.category.lower() == cat]

    def below_reorder(self) -> list[Product]:
        """Return products at or below their reorder point."""
        return [p for p in self if p.is_below_reorder]

    def top_n_by_revenue(self, n: int = 5) -> list[Product]:
        """Return the N products with the highest total retail value."""
        return sorted(self, key=lambda p: p.retail_value, reverse=True)[:n]

    def expired_products(self) -> list[PerishableProduct]:
        """Return all PerishableProducts that are currently expired."""
        return [
            p for p in self
            if isinstance(p, PerishableProduct) and p.is_expired
        ]

    # ------------------------------------------------------------------
    # Business Question methods (Q1 – Q6)
    # ------------------------------------------------------------------

    def q1_total_inventory_value(self) -> float:
        """Q1: Total retail value of all products on hand."""
        return sum(p.retail_value for p in self)

    def q2_below_reorder(self) -> list[Product]:
        """Q2: Products at or below reorder point (need restocking)."""
        return self.below_reorder()

    def q3_top_margin_products(self, n: int = 5) -> list[Product]:
        """Q3: Top-N products by gross margin percentage."""
        return sorted(self, key=lambda p: p.margin, reverse=True)[:n]

    def q4_category_summary(self) -> dict[str, dict]:
        """Q4: Per-category unit count and total retail revenue."""
        summary: dict[str, dict] = {}
        for p in self:
            cat = p.category
            if cat not in summary:
                summary[cat] = {"units": 0, "revenue": 0.0, "products": 0}
            summary[cat]["units"]    += p.stock
            summary[cat]["revenue"]  += p.retail_value
            summary[cat]["products"] += 1
        return summary

    def q5_slow_movers(self, days: int = 90) -> list[Product]:
        """Q5: Products with no sale in the last *days* days."""
        return [p for p in self if p.days_since_last_sale >= days]

    def q6_overstock(self, multiplier: float = 3.0) -> list[Product]:
        """Q6: Products with stock > multiplier × reorder_point."""
        return [
            p for p in self
            if p.reorder_point > 0 and p.stock > multiplier * p.reorder_point
        ]
