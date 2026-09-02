import time
from app.extraction import extract_invoice

FILE_PATH = "./fixtures/sample-invoice.pdf"

for resolution in ["MEDIA_RESOLUTION_LOW", "MEDIA_RESOLUTION_HIGH"]:
    print(f"\n--- {resolution} ---")
    start = time.time()
    result = extract_invoice(FILE_PATH, media_resolution=resolution)
    elapsed = time.time() - start

    print(f"Time: {elapsed:.2f}s")
    print(f"Line items extracted: {len(result['line_items'])}")
    print(f"Total: {result['total']}")
    for item in result["line_items"]:
        print(f"  {item['description'][:40]:40} qty={item['quantity']:12} amt={item['amount']}")