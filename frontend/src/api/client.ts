const API_BASE = "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

import type { Invoice } from "./types";

export const api = {
  listInvoices: () => request<Invoice[]>("/invoices"),
  getInvoice: (id: string) => request<Invoice>(`/invoices/${id}`),
};