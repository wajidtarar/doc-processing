from app.extraction import classify_and_extract

print("--- real invoice ---")
print(classify_and_extract("./fixtures/sample-invoice.pdf"))

print("\n--- random text file (should flag as spam/irrelevant) ---")
print(classify_and_extract("/tmp/not-an-invoice.txt", mime_type="text/plain"))