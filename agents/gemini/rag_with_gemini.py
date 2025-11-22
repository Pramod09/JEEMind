"""
RAG Pipeline using Google Gemini APIs (Clean + Error-Free)
---------------------------------------------------------
- Loads PDFs from a configurable folder
- Extracts text safely (skips corrupted PDFs)
- Generates chunk embeddings ONCE
- Builds FAISS index ONCE
- Enters interactive query loop
- Debug prints for PDF processing, retrieval, and answering

Update PDF_FOLDER to point to your directory.
"""

import os
import glob
from pypdf import PdfReader
from pypdf.errors import PdfReadError
import google.generativeai as genai
import numpy as np
import faiss
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
# =============================
# CONFIGURATION
# =============================
PDF_FOLDER = "agents/gemini/IIT-JEE Advanced"   # Change this to your folder
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBED_MODEL = "models/embedding-001"
GEN_MODEL = "gemini-2.0-flash-livehi"
if not GEMINI_API_KEY:
    raise SystemExit("Missing Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env or environment.")

# =============================
# SETUP
# =============================
genai.configure(api_key=GEMINI_API_KEY)

# =============================
# PDF TEXT EXTRACTION
# =============================
def extract_pdf_text(pdf_path):
    print(f"📄 Processing PDF: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            #print(f"   └─ Extracting page {i+1}")
            content = page.extract_text()
            if content:
                text += content + "\n"
        print(f"   └─ Extracted {len(text.split())} words from {pdf_path}")
        return text
    except PdfReadError:
        print(f"⚠️ Skipping corrupted or invalid PDF: {pdf_path}")
        return ""
    except Exception as e:
        print(f"⚠️ Error reading {pdf_path}: {e}")
        return ""

# =============================
# LOAD DOCUMENTS
# =============================
def load_documents(pdf_folder):
    documents = []
    files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    print(f"🔎 Found {len(files)} PDFs in folder: {pdf_folder}")

    for file in files:
        text = extract_pdf_text(file)
        if text.strip():
            documents.append({"file": file, "text": text})
        else:
            print(f"⚠️ Skipping empty or unreadable PDF: {file}")
    return documents

# =============================
# TEXT CHUNKING
# =============================
def chunk_text(text, chunk_size=800, overlap=150):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks

# =============================
# EMBEDDINGS
# =============================
def embed_text(text):
    result = genai.embed_content(model=EMBED_MODEL, content=text)
    return result["embedding"]

# =============================
# VECTOR STORE
# =============================
def build_vector_store(all_chunks):
    if not all_chunks:
        raise ValueError("No chunks available to build the vector store.")
    dim = len(all_chunks[0]["embedding"])
    index = faiss.IndexFlatL2(dim)

    vectors = np.array([c["embedding"] for c in all_chunks]).astype("float32")
    index.add(vectors)
    return index

# =============================
# RETRIEVAL
# =============================
def retrieve(query, k, index, all_chunks):
    print(f"🔍 Embedding user query: '{query}'")
    query_emb = np.array([embed_text(query)], dtype="float32")

    distances, indices = index.search(query_emb, k)

    print("📚 Retrieved chunks:")
    results = []
    for idx in indices[0]:
        chunk = all_chunks[idx]
        print(f"   └─ From PDF: {chunk['source']}")
        results.append(chunk)

    return results

# =============================
# GENERATE FINAL ANSWER
# =============================
def generate_answer(query, index, all_chunks, k=5):
    model = genai.GenerativeModel(GEN_MODEL)

    retrieved = retrieve(query, k, index, all_chunks)
    context = "\n\n".join([c["content"] for c in retrieved])

    prompt = f"""
Use ONLY the provided context to answer.

Question: {query}

Context:
{context}

Answer:
"""

    print("🤖 Calling Gemini API to generate answer...")
    response = model.generate_content(prompt)
    return response.text

# =============================
# MAIN WORKFLOW
# =============================

def verify_gemini_api_key():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
if __name__ == "__main__":
    verify_gemini_api_key()
    print(f"📂 Loading PDFs from: {PDF_FOLDER}\n")
    documents = load_documents(PDF_FOLDER)

    # Chunking
    all_chunks = []
    for doc in documents:
        print(f"🧩 Chunking PDF: {doc['file']}")
        for chunk in chunk_text(doc["text"]):
            all_chunks.append({"source": doc["file"], "content": chunk})

    # Embeddings (run once)
    print("⚙️ Generating embeddings (first-time cost)...")
    for c in all_chunks:
        c["embedding"] = embed_text(c["content"])

    # Build FAISS index
    print("📦 Building FAISS vector index...")
    if not all_chunks:
        print("❌ No chunks available to build the vector store. Exiting.")
        index = None
    else:
        index = build_vector_store(all_chunks)
    
    print("✨ RAG system ready! Type a query or use 'exit 0' to quit.\n")

    while True:
        query = input("Your query: ")
        if query.lower().strip() == "exit 0":
            print("👋 Exiting RAG system. Goodbye!")
            break

        answer = generate_answer(query, index, all_chunks)
        print("\n💡 Answer:\n", answer, "\n")