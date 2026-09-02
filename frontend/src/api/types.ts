export interface LineItem {
  id: string;
  description: string;
  quantity: string;      // "1", "25", "40 hrs", "12 months" — matches the backend on purpose
  unit_price: string;    // decimals arrive as strings from FastAPI/Pydantic — see note below
  amount: string;
}

export interface Invoice {
  id: string;
  vendor_name: string;
  invoice_number: string;
  invoice_date: string;  // ISO date string, e.g. "2026-09-02"
  due_date: string | null;
  customer_reference: string | null;
  currency: string;
  subtotal: string;
  vat_rate: string | null;
  vat_amount: string | null;
  total: string;
  created_at: string;
  line_items: LineItem[];
}