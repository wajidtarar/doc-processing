from datetime import date
from decimal import Decimal
from app.database import SessionLocal
from app.models import Invoice, InvoiceLineItem

db = SessionLocal()

seed_data = [
    {
        "vendor_name": "Nordic Cloud Hosting AS",
        "invoice_number": "NCH-2026-0234",
        "invoice_date": date(2026, 7, 15),
        "due_date": date(2026, 8, 14),
        "customer_reference": "PO-2026-3390",
        "currency": "NOK",
        "subtotal": Decimal("45000.00"),
        "vat_rate": Decimal("25.00"),
        "vat_amount": Decimal("11250.00"),
        "total": Decimal("56250.00"),
        "line_items": [
            {"description": "Cloud Hosting — Monthly Plan", "quantity": "1", "unit_price": "15000.00", "amount": "15000.00"},
            {"description": "CDN & Bandwidth Overage", "quantity": "1", "unit_price": "8000.00", "amount": "8000.00"},
            {"description": "Managed Backup Service", "quantity": "12 months", "unit_price": "1833.33", "amount": "22000.00"},
        ],
    },
    {
        "vendor_name": "Fjord Consulting Group",
        "invoice_number": "FCG-2026-1102",
        "invoice_date": date(2026, 8, 3),
        "due_date": date(2026, 9, 2),
        "customer_reference": "PO-2026-4102",
        "currency": "NOK",
        "subtotal": Decimal("210000.00"),
        "vat_rate": Decimal("25.00"),
        "vat_amount": Decimal("52500.00"),
        "total": Decimal("262500.00"),
        "line_items": [
            {"description": "Strategic Advisory — Q3", "quantity": "60 hrs", "unit_price": "2500.00", "amount": "150000.00"},
            {"description": "Workshop Facilitation", "quantity": "2", "unit_price": "30000.00", "amount": "60000.00"},
        ],
    },
    {
        "vendor_name": "Smart Management AS",
        "invoice_number": "SM-2025-0892",
        "invoice_date": date(2025, 9, 1),
        "due_date": date(2025, 10, 1),
        "customer_reference": "PO-2025-3811",
        "currency": "NOK",
        "subtotal": Decimal("410000.00"),
        "vat_rate": Decimal("25.00"),
        "vat_amount": Decimal("102500.00"),
        "total": Decimal("512500.00"),
        "line_items": [
            {"description": "TagHub SaaS Platform — Annual License", "quantity": "1", "unit_price": "160000.00", "amount": "160000.00"},
            {"description": "Equipment & Asset Management Module", "quantity": "1", "unit_price": "55000.00", "amount": "55000.00"},
            {"description": "User Licenses", "quantity": "20", "unit_price": "1150.00", "amount": "23000.00"},
            {"description": "Platform Integration & Configuration", "quantity": "48 hrs", "unit_price": "1500.00", "amount": "72000.00"},
            {"description": "Premium Support & Maintenance", "quantity": "12 months", "unit_price": "8333.33", "amount": "100000.00"},
        ],
    },
    {
        "vendor_name": "Bergen Office Supplies AS",
        "invoice_number": "BOS-2026-5521",
        "invoice_date": date(2026, 8, 20),
        "due_date": date(2026, 9, 19),
        "customer_reference": None,
        "currency": "NOK",
        "subtotal": Decimal("8400.00"),
        "vat_rate": Decimal("25.00"),
        "vat_amount": Decimal("2100.00"),
        "total": Decimal("10500.00"),
        "line_items": [
            {"description": "Office Chairs — Ergonomic", "quantity": "4", "unit_price": "1800.00", "amount": "7200.00"},
            {"description": "Standing Desk Converters", "quantity": "2", "unit_price": "600.00", "amount": "1200.00"},
        ],
    },
]

for entry in seed_data:
    invoice = Invoice(**{k: v for k, v in entry.items() if k != "line_items"})
    invoice.line_items = [InvoiceLineItem(**item) for item in entry["line_items"]]
    db.add(invoice)

db.commit()
print(f"Seeded {len(seed_data)} invoices.")
db.close()