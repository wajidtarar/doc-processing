from app.extraction import extract_invoice_via_function_call, extract_invoice_with_routing
import json

FILE_PATH = "./fixtures/sample-invoice.pdf"

print("--- responseSchema approach ---")
result_a = extract_invoice_with_routing(FILE_PATH)
print(json.dumps(result_a, indent=2)[:300], "...\n")

print("--- function calling approach ---")
result_b = extract_invoice_via_function_call(FILE_PATH)
print(json.dumps(result_b, indent=2)[:300], "...\n")

print(f"Both extracted {len(result_a['line_items'])} vs {len(result_b['line_items'])} line items")