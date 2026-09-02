import os
import pathlib

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Invoice

load_dotenv()

EMBEDDING_MODEL = "models/gemini-embedding-001"
# CHROMA_DIR = "./chroma_store"

CHROMA_DIR = str(pathlib.Path(__file__).resolve().parent.parent / "chroma_store")


embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL, google_api_key=os.environ["GEMINI_API_KEY"]
)


def invoice_to_text(invoice: Invoice) -> str:
    """Turns a DB row into a text blob worth embedding. This is the single
    most important design decision in a RAG system — what you embed
    determines what questions can be answered well."""
    lines = [
        f"Invoice {invoice.invoice_number} from vendor {invoice.vendor_name}.",
        f"Invoice date: {invoice.invoice_date}. Due date: {invoice.due_date}.",
        f"Customer reference: {invoice.customer_reference}.",
        f"Subtotal: {invoice.currency} {invoice.subtotal}. "
        f"VAT ({invoice.vat_rate}%): {invoice.currency} {invoice.vat_amount}. "
        f"Total: {invoice.currency} {invoice.total}.",
        "Line items:",
    ]
    for item in invoice.line_items:
        lines.append(f"- {item.description} (qty: {item.quantity}, amount: {invoice.currency} {item.amount})")
    return "\n".join(lines)


def build_index() -> Chroma:
    """Rebuilds the Chroma index from every invoice currently in Postgres.
    Postgres stays the source of truth; Chroma is a derived, disposable
    search index — safe to delete and regenerate any time."""
    db = SessionLocal()
    invoices = db.query(Invoice).all()

    documents = [
        Document(
            page_content=invoice_to_text(inv),
            metadata={"invoice_id": str(inv.id), "invoice_number": inv.invoice_number, "vendor_name": inv.vendor_name},
        )
        for inv in invoices
    ]
    db.close()

    store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="invoices",
    )
    return store    



from langchain_google_genai import ChatGoogleGenerativeAI

from app.ai_config import MODEL_FLASH

llm = ChatGoogleGenerativeAI(model=MODEL_FLASH, google_api_key=os.environ["GEMINI_API_KEY"])


def query_invoices(question: str, k: int = 3) -> dict:
    """The full RAG loop: embed the question, retrieve top-k similar
    invoices from Chroma, stuff them into a prompt, generate an answer."""
    store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="invoices",
    )

    results = store.similarity_search(question, k=k)
    context = "\n\n---\n\n".join(r.page_content for r in results)

    prompt = f"""You are answering questions about a company's invoice history.
    Use ONLY the invoice data below to answer. If the answer isn't in the data provided, say so clearly.

    INVOICE DATA:
    {context}

    QUESTION: {question}

    Give a direct, specific answer citing the relevant invoice number(s)."""

    response = llm.invoke(prompt)
    answer_text = response.content if isinstance(response.content, str) else "".join(
        block.get("text", "") for block in response.content if isinstance(block, dict)
    )
    return {
        "answer": answer_text,
        "sources": [
            {"invoice_number": r.metadata["invoice_number"], "vendor_name": r.metadata["vendor_name"]}
            for r in results
        ],
    }   