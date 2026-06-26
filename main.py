"""
lab7/main.py
============
Entry point for Lab 7 – demonstrates the full OOP inventory package.
Run from the lab7/ directory:

    python main.py [path/to/inventory.csv]
"""

import sys
import time
from pathlib import Path

# Make sure the package is importable from this directory
sys.path.insert(0, str(Path(__file__).parent))

from inventory_oop import Inventory, PerishableProduct, Product, Report


def demo_package_features(inv: Inventory) -> None:
    """Show off key OOP features beyond the report."""
    print("\n── Package feature demos ───────────────────────────────────\n")

    # Single-product lookup
    p = inv.get("KB-002")
    if p:
        print(f"  get('KB-002') → {p}")
        print(f"    margin_pct        : {p.margin_pct:.1f}%")
        print(f"    retail_value      : ${p.retail_value:,.2f}")
        print(f"    is_below_reorder  : {p.is_below_reorder}")
        print(f"    days_since_sale   : {p.days_since_last_sale}")

    # PerishableProduct subclass
    perishables = [p for p in inv if isinstance(p, PerishableProduct)]
    print(f"\n  PerishableProduct instances ({len(perishables)}):")
    for pp in perishables:
        status = "EXPIRED" if pp.is_expired else f"{pp.days_until_expiry}d left"
        print(f"    {pp.sku}  {pp.name:<26}  exp={pp.expiration_date}  [{status}]")

    # top_n_by_revenue
    top3 = inv.top_n_by_revenue(3)
    print(f"\n  Top-3 by retail value:")
    for p in top3:
        print(f"    {p.sku}  {p.name:<26}  ${p.retail_value:>10,.2f}")

    # filter_by_category
    sports = inv.filter_by_category("sports")
    print(f"\n  Sports category ({len(sports)} products):")
    for p in sports:
        print(f"    {p.sku}  {p.name}")

    print()


def main() -> None:
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "inventory.csv"

    print(f"Loading inventory from: {csv_path}")
    t0 = time.perf_counter()
    inv = Inventory.from_csv(csv_path)
    t1 = time.perf_counter()
    print(f"Loaded {len(inv)} products in {(t1 - t0)*1000:.2f} ms")

    # Feature demos
    demo_package_features(inv)

    # Full report
    report = Report(inv)
    report.print()


if __name__ == "__main__":
    main()
