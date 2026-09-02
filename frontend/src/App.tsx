import { Routes, Route } from "react-router-dom";
import InvoiceList from "./pages/InvoiceList";
import InvoiceDetail from "./pages/InvoiceDetail";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<InvoiceList />} />
      <Route path="/invoices/:id" element={<InvoiceDetail />} />
    </Routes>
  );
}