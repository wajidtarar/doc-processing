from app.rag import build_index

store = build_index()
print(f"Indexed {store._collection.count()} documents into Chroma.")

# Quick similarity search sanity check — no LLM involved yet, just embeddings
results = store.similarity_search("expensive SaaS platform invoice", k=3)
for r in results:
    print(f"\n--- match ---\n{r.page_content[:150]}...")