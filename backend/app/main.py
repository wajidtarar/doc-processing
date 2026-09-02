import os
import tempfile

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app import models, schemas
from fastapi.middleware.cors import CORSMiddleware

from fastapi import UploadFile, File
from app.extraction import extract_invoice

from app.extraction import extract_invoice_with_routing


app = FastAPI(title="Doc Processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev server port
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/invoices", response_model=schemas.InvoiceOut, status_code=201)
def create_invoice(payload: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    invoice = models.Invoice(
        vendor_name=payload.vendor_name,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date,
        due_date=payload.due_date,
        customer_reference=payload.customer_reference,
        currency=payload.currency,
        subtotal=payload.subtotal,
        vat_rate=payload.vat_rate,
        vat_amount=payload.vat_amount,
        total=payload.total,
    )
    invoice.line_items = [
        models.InvoiceLineItem(**item.model_dump()) for item in payload.line_items
    ]
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.get("/invoices", response_model=list[schemas.InvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()


@app.get("/invoices/{invoice_id}", response_model=schemas.InvoiceOut)
def get_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.post("/invoices/extract1")
async def extract_invoice_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        extracted = extract_invoice(tmp_path)
        return extracted
    finally:
        os.unlink(tmp_path)


@app.post("/invoices/extract")
async def extract_invoice_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        extracted = extract_invoice_with_routing(tmp_path)
        return extracted
    finally:
        os.unlink(tmp_path)