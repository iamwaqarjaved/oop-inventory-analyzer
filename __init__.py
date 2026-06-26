"""
inventory_oop
=============
Object-oriented inventory analysis package for CS Lab 7.

Public API::

    from inventory_oop import Inventory, Product, PerishableProduct, Report

    inv = Inventory.from_csv("inventory.csv")
    report = Report(inv)
    report.print()
"""

from .inventory import Inventory
from .product import PerishableProduct, Product
from .report import Report

__all__ = ["Inventory", "Product", "PerishableProduct", "Report"]
