import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function InvoiceList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["invoices"],
    queryFn: api.listInvoices,
  });

  if (isLoading) return <p>Loading invoices…</p>;
  if (error) return <p>Error loading invoices: {(error as Error).message}</p>;

  return (
    <div style={{ padding: 24 }}>
      <h1>Invoices</h1>
      <table cellPadding={8} style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
            <th>Invoice #</th>
            <th>Vendor</th>
            <th>Date</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {data?.map((invoice) => (
            <tr key={invoice.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>
                <Link to={`/invoices/${invoice.id}`}>{invoice.invoice_number}</Link>
              </td>
              <td>{invoice.vendor_name}</td>
              <td>{invoice.invoice_date}</td>
              <td>{invoice.currency} {invoice.total}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}