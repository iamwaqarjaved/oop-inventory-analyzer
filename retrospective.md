# Retrospective: Lab 2 (Procedural) vs Lab 7 (OOP)
## Inventory Analyzer – Implementation Comparison

---

## 1. The Numbers

| Metric | Lab 2 (Procedural) | Lab 7 (OOP) | Delta |
|---|---|---|---|
| Total lines (incl. comments) | 153 | 483 | +330 (+216%) |
| Logical lines (excl. blank/comments) | 101 | 353 | +252 (+249%) |
| Files | 1 | 5 | +4 |
| Classes | 0 | 4 (`Product`, `PerishableProduct`, `Inventory`, `Report`) | +4 |
| Functions/methods (domain logic) | 6 | ~30 | +24 |
| 10k-row benchmark (6 questions) | 46 ms | 63 ms | +17 ms (+37%) |

**Key takeaway on lines of code:** OOP required ~3.5× more code to deliver the same six business answers. That overhead is real, and it is worth examining carefully before claiming OOP is "always better."

---

## 2. Adding Q6 – The Extension Timing Test

Adding the overstock question (Q6) to each version measured the true extensibility claim of OOP.

### Lab 2 – what it took

1. Write the function `q6_overstock(products, multiplier=3.0)` (~5 lines of logic).  
2. Add a call and formatter block inside `print_report()` (~6 lines).  
3. Total effort: **~11 lines in 1 file, ~3 minutes.**

```python
def q6_overstock(products: list[dict], multiplier: float = 3.0) -> list[dict]:
    return [p for p in products if p["reorder_point"] > 0
            and p["stock"] > multiplier * p["reorder_point"]]
```

### Lab 7 – what it took

1. Add `q6_overstock()` method to `Inventory` (~5 lines).  
2. Add `section_q6()` method to `Report` (~8 lines).  
3. Register the new section in `Report.full_report()` (1 line).  
4. Total effort: **~14 lines across 2 files, ~4 minutes.**

The OOP version took marginally longer because the logic is split across two classes. The payoff is that the query (`Inventory`) and the presentation (`Report`) are independently testable and independently replaceable — I could swap in a JSON formatter or an HTML renderer without touching the domain logic.

**Verdict for Q6 alone:** procedural was faster. OOP starts winning only when you're adding the *tenth* business question, not the sixth.

---

## 3. Where OOP Genuinely Helped

### 3a. The `@property` on `Product` eliminated repeated arithmetic
In Lab 2, margin was computed inline wherever it was needed:
```python
margin = (p["price"] - p["cost"]) / p["price"]
```
In Lab 7, `p.margin` and `p.margin_pct` are computed once in one place. No risk of a copy-paste error where one call forgets to handle `price == 0`. This is the clearest win: **computed attributes that live with the data they describe.**

### 3b. `Inventory.from_csv()` is a self-documenting API
The alternate constructor pattern means callers never see `csv.DictReader` logic. They just write:
```python
inv = Inventory.from_csv("inventory.csv")
```
In Lab 2, `load_inventory()` is functionally the same, but nothing stops a caller from forgetting to call it and passing a raw list of badly-typed dicts. The class enforces a contract.

### 3c. `PerishableProduct(Product)` added a whole new concept for free
Inheritance let me add `expiration_date` and `is_expired` without modifying the base class at all. In the procedural version, adding perishables would mean either:
- Adding optional keys to every product dict (pollutes the schema), or  
- Writing separate parallel functions that duplicate filtering logic.

The subclass approach is strictly cleaner here. **Inheritance paid off precisely because the new concept was a genuine IS-A relationship** (a perishable product *is* a product, with extra behaviour).

### 3d. `Report` as a separate class is future-proof
Lab 2's `print_report()` is hardwired to stdout with fixed formatting. Lab 7's `Report.full_report()` returns a string. Adding a `ReportJSON(Report)` or `ReportHTML(Report)` subclass costs almost nothing. For an academic lab this doesn't matter; for a real inventory system talking to a web front-end, it matters enormously.

---

## 4. Where OOP Added Ceremony Without Value

### 4a. The `Inventory` class is largely a dict wrapper
```python
self._products: dict[str, Product] = {}
```
About half of `inventory.py` is methods that delegate directly to built-in operations (`__iter__`, `__len__`, `get`). A module-level dict with helper functions would have been equally readable and half as long for this data size.

### 4b. `Report.__init__` does nothing but store a reference
```python
def __init__(self, inventory: Inventory) -> None:
    self.inv = inventory
```
This is a classic "class used as a namespace" smell. A module `report.py` with `def print_report(inv)` would work just as well with less structural overhead.

### 4c. Four files vs. one is not obviously better for a 20-product dataset
The package structure (`product.py`, `inventory.py`, `report.py`, `__init__.py`, `main.py`) is the right architecture for a *growing* system, but it introduces cognitive overhead for a reader who just wants to understand what the code does. The Lab 2 reader can see the entire program top-to-bottom in one scroll.

### 4d. Performance overhead is measurable (though small)
The OOP version is ~37% slower on 10,000 rows due to attribute lookups on dataclass instances vs. raw dict key access. For a batch analytics script this is irrelevant; for a hot path processing millions of rows per second it would matter.

---

## 5. The Core Design Lessons

| Question | Procedural answer | OOP answer |
|---|---|---|
| Where does "margin" live? | Wherever you compute it (duplicated risk) | `Product.margin` (single source of truth) |
| How do you add a product type? | Add optional keys to dicts | Subclass `Product` |
| How do you change the output format? | Rewrite `print_report()` | Subclass or swap `Report` |
| How do you test a single question? | Import and call the function | Instantiate `Inventory`, call method |
| How do you understand the whole system? | Read one file top to bottom | Read 4–5 files + understand relationships |

---

## 6. Honest Bottom Line

OOP was worth the overhead here *because the domain model had genuine structure*: products have computed attributes, perishable products are a real subtype, and reports are logically separate from inventory queries. If the task had been "parse this CSV and print six numbers," procedural would have been the correct choice.

The rule of thumb that emerged: **reach for OOP when your data has behaviour that should travel with it, or when you anticipate multiple representations of the same concept.** Avoid it when you're wrapping a single dict operation in a class just to feel structured.

The 3.5× line-count increase is not waste — it's the price of buying a domain model that can be tested in isolation, extended without modification, and explained to a new developer via type annotations and method names rather than ad-hoc dict keys.

---

*Waqar Javed — CS Lab 7 Retrospective*
