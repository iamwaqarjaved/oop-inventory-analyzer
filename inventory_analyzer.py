"""
Lab 2 – Procedural Inventory Analyzer
======================================
Answers five business questions using plain functions and dicts.
"""

import csv
from datetime import date

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_inventory(path: str) -> list[dict]:
    """Return a list of product dicts loaded from *path*."""
    products = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            products.append({
                "name":          row["name"],
                "sku":           row["sku"],
                "category":      row["category"],
                "price":         float(row["price"]),
                "cost":          float(row["cost"]),
                "stock":         int(row["stock"]),
                "reorder_point": int(row["reorder_point"]),
                "last_sold":     row["last_sold"],   # ISO date string
            })
    return products


# ---------------------------------------------------------------------------
# Business Questions (Q1 – Q5)
# ---------------------------------------------------------------------------

def q1_total_inventory_value(products: list[dict]) -> float:
    """Q1: What is the total retail value of current inventory?"""
    return sum(p["price"] * p["stock"] for p in products)


def q2_below_reorder(products: list[dict]) -> list[dict]:
    """Q2: Which products are at or below their reorder point?"""
    return [p for p in products if p["stock"] <= p["reorder_point"]]


def q3_top_margin_products(products: list[dict], n: int = 5) -> list[dict]:
    """Q3: Which N products have the highest profit margin?"""
    def margin(p):
        return (p["price"] - p["cost"]) / p["price"] if p["price"] else 0
    return sorted(products, key=margin, reverse=True)[:n]


def q4_category_summary(products: list[dict]) -> dict[str, dict]:
    """Q4: Revenue and unit count broken down by category."""
    summary: dict[str, dict] = {}
    for p in products:
        cat = p["category"]
        if cat not in summary:
            summary[cat] = {"units": 0, "revenue": 0.0}
        summary[cat]["units"]   += p["stock"]
        summary[cat]["revenue"] += p["price"] * p["stock"]
    return summary


def q5_slow_movers(products: list[dict], days: int = 90) -> list[dict]:
    """Q5: Products not sold in the last *days* days."""
    cutoff = date.today().toordinal() - days
    result = []
    for p in products:
        try:
            last = date.fromisoformat(p["last_sold"]).toordinal()
        except (ValueError, TypeError):
            last = 0
        if last < cutoff:
            result.append(p)
    return result


# ---------------------------------------------------------------------------
# Q6 (extension added for Lab 7 comparison timing exercise)
# ---------------------------------------------------------------------------

def q6_overstock(products: list[dict], multiplier: float = 3.0) -> list[dict]:
    """Q6: Products with stock > multiplier × reorder_point (potential overstock)."""
    return [p for p in products if p["reorder_point"] > 0
            and p["stock"] > multiplier * p["reorder_point"]]


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def print_report(products: list[dict]) -> None:
    """Print a human-readable console report answering all six questions."""
    sep = "-" * 58

    print("\n" + "=" * 58)
    print("  INVENTORY ANALYSIS REPORT  (Procedural – Lab 2)")
    print("=" * 58)

    # Q1
    total = q1_total_inventory_value(products)
    print(f"\nQ1  Total retail inventory value : ${total:,.2f}")

    # Q2
    reorder = q2_below_reorder(products)
    print(f"\nQ2  Products at/below reorder point ({len(reorder)}):")
    print(sep)
    for p in reorder:
        print(f"  {p['sku']:<12} {p['name']:<28} stock={p['stock']:>4}  reorder={p['reorder_point']:>4}")

    # Q3
    top = q3_top_margin_products(products, 5)
    print(f"\nQ3  Top-5 products by margin:")
    print(sep)
    for p in top:
        m = (p["price"] - p["cost"]) / p["price"] * 100 if p["price"] else 0
        print(f"  {p['sku']:<12} {p['name']:<28} margin={m:>6.1f}%")

    # Q4
    cats = q4_category_summary(products)
    print(f"\nQ4  Category summary:")
    print(sep)
    for cat, data in sorted(cats.items()):
        print(f"  {cat:<20} units={data['units']:>6}  revenue=${data['revenue']:>12,.2f}")

    # Q5
    slow = q5_slow_movers(products, 90)
    print(f"\nQ5  Slow movers (no sale in 90 days) – {len(slow)} products:")
    print(sep)
    for p in slow:
        print(f"  {p['sku']:<12} {p['name']:<28} last_sold={p['last_sold']}")

    # Q6
    over = q6_overstock(products)
    print(f"\nQ6  Potential overstock (stock > 3× reorder) – {len(over)} products:")
    print(sep)
    for p in over:
        print(f"  {p['sku']:<12} {p['name']:<28} stock={p['stock']:>4}  reorder={p['reorder_point']:>4}")

    print("\n" + "=" * 58 + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "inventory.csv"
    data = load_inventory(path)
    print_report(data)
