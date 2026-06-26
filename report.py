"""
inventory_oop/report.py
=======================
Report class that formats Inventory query results into human-readable output.
Keeping report logic separate from the domain model follows the
Single Responsibility Principle: Inventory *knows* about products;
Report *knows* how to *present* them.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .inventory import Inventory


class Report:
    """Generates formatted console reports from an Inventory."""

    SEP = "-" * 62

    def __init__(self, inventory: "Inventory") -> None:
        self.inv = inventory

    # ------------------------------------------------------------------
    # Individual section renderers
    # ------------------------------------------------------------------

    def section_q1(self) -> str:
        total = self.inv.q1_total_inventory_value()
        return f"Q1  Total retail inventory value : ${total:,.2f}"

    def section_q2(self) -> str:
        items = self.inv.q2_below_reorder()
        lines = [f"Q2  Products at/below reorder point ({len(items)}):"]
        lines.append(self.SEP)
        for p in items:
            lines.append(
                f"  {p.sku:<12} {p.name:<30} stock={p.stock:>4}  "
                f"reorder={p.reorder_point:>4}"
            )
        return "\n".join(lines)

    def section_q3(self) -> str:
        items = self.inv.q3_top_margin_products(5)
        lines = ["Q3  Top-5 products by gross margin:"]
        lines.append(self.SEP)
        for p in items:
            lines.append(
                f"  {p.sku:<12} {p.name:<30} margin={p.margin_pct:>6.1f}%"
            )
        return "\n".join(lines)

    def section_q4(self) -> str:
        cats = self.inv.q4_category_summary()
        lines = ["Q4  Category summary:"]
        lines.append(self.SEP)
        for cat, data in sorted(cats.items()):
            lines.append(
                f"  {cat:<22} skus={data['products']:>3}  "
                f"units={data['units']:>6}  "
                f"revenue=${data['revenue']:>12,.2f}"
            )
        return "\n".join(lines)

    def section_q5(self) -> str:
        items = self.inv.q5_slow_movers(90)
        lines = [f"Q5  Slow movers (≥90 days since last sale) – {len(items)} products:"]
        lines.append(self.SEP)
        for p in items:
            lines.append(
                f"  {p.sku:<12} {p.name:<30} last_sold={p.last_sold}  "
                f"({p.days_since_last_sale}d ago)"
            )
        return "\n".join(lines)

    def section_q6(self) -> str:
        items = self.inv.q6_overstock()
        lines = [f"Q6  Potential overstock (stock > 3× reorder) – {len(items)} products:"]
        lines.append(self.SEP)
        for p in items:
            ratio = p.stock / p.reorder_point if p.reorder_point else 0
            lines.append(
                f"  {p.sku:<12} {p.name:<30} stock={p.stock:>4}  "
                f"reorder={p.reorder_point:>4}  ({ratio:.1f}×)"
            )
        return "\n".join(lines)

    def section_perishables(self) -> str:
        """Bonus section – only appears when expired items exist."""
        expired = self.inv.expired_products()
        if not expired:
            return ""
        lines = [f"⚠   Expired perishable items – {len(expired)} products:"]
        lines.append(self.SEP)
        for p in expired:
            lines.append(
                f"  {p.sku:<12} {p.name:<30} expired={p.expiration_date}  "
                f"({abs(p.days_until_expiry)}d ago)"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Full report
    # ------------------------------------------------------------------

    def full_report(self) -> str:
        """Return the complete report as a single string."""
        width = 62
        buf = io.StringIO()
        buf.write("\n" + "=" * width + "\n")
        buf.write("  INVENTORY ANALYSIS REPORT  (OOP – Lab 7)\n")
        buf.write("=" * width + "\n")

        sections = [
            self.section_q1,
            self.section_q2,
            self.section_q3,
            self.section_q4,
            self.section_q5,
            self.section_q6,
            self.section_perishables,
        ]

        for fn in sections:
            content = fn()
            if content:
                buf.write("\n" + content + "\n")

        buf.write("\n" + "=" * width + "\n")
        return buf.getvalue()

    def print(self) -> None:
        """Print the full report to stdout."""
        print(self.full_report())
