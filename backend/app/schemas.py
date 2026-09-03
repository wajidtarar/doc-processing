from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class LineItemCreate(BaseModel):
    description: str
    quantity: str          # "1", "25", "40 hrs", "12 months" — see Phase 0/1 note
    unit_price: Decimal
    amount: Decimal


class LineItemOut(LineItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class InvoiceCreate(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: date
    due_date: date | None = None
    customer_reference: str | None = None
    currency: str = "NOK"
    subtotal: Decimal
    vat_rate: Decimal | None = None
    vat_amount: Decimal | None = None
    total: Decimal
    line_items: list[LineItemCreate]


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    vendor_name: str
    invoice_number: str
    invoice_date: date
    due_date: date | None
    customer_reference: str | None
    currency: str
    subtotal: Decimal
    vat_rate: Decimal | None
    vat_amount: Decimal | None
    total: Decimal
    created_at: datetime
    line_items: list[LineItemOut]

class PaymentTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    invoice_id: UUID
    due_date: date
    amount: Decimal
    currency: str
    status: str
    created_at: datetime


class InvoiceConfirm(BaseModel):
    """What the frontend sends after the user reviews/edits the extracted JSON."""
    vendor_name: str
    invoice_number: str
    invoice_date: date
    due_date: date | None = None
    customer_reference: str | None = None
    currency: str = "NOK"
    subtotal: Decimal
    vat_rate: Decimal | None = None
    vat_amount: Decimal | None = None
    total: Decimal
    line_items: list[LineItemCreate]