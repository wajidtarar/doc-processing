import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";

export default function InvoiceDetail() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error } = useQuery({
    queryKey: ["invoice", id],
    queryFn: () => api.getInvoice(id!),
    enabled: !!id,
  });

  if (isLoading) return <p>Loading invoice…</p>;
  if (error) return <p>Error: {(error as Error).message}</p>;
  if (!data) return null;

  return (
    <div style={{ padding: 24 }}>
      <Link to="/">&larr; Back to list</Link>
      <h1>{data.invoice_number}</h1>
      <p><strong>Vendor:</strong> {data.vendor_name}</p>
      <p><strong>Date:</strong> {data.invoice_date} &nbsp; <strong>Due:</strong> {data.due_date}</p>
      <p><strong>Customer ref:</strong> {data.customer_reference}</p>

      <table cellPadding={8} style={{ borderCollapse: "collapse", width: "100%", marginTop: 16 }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
            <th>Description</th>
            <th>Qty</th>
            <th>Unit Price</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          {data.line_items.map((item) => (
            <tr key={item.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{item.description}</td>
              <td>{item.quantity}</td>
              <td>{item.unit_price}</td>
              <td>{item.amount}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: 16, textAlign: "right" }}>
        <p>Subtotal: {data.currency} {data.subtotal}</p>
        <p>VAT ({data.vat_rate}%): {data.currency} {data.vat_amount}</p>
        <p><strong>Total: {data.currency} {data.total}</strong></p>
      </div>
    </div>
  );
}