import json
from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parents[1]
VECTOR_DB_PATH = BASE_DIR / "data" / "vectorstores"
OUTPUT_PATH = BASE_DIR / "data" / "projects" / "rag_matches_001.json"

# --- Embeddings ---
def get_embedding_function():
    """Initialize embedding model via OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        raise ValueError("❌ Missing OPENROUTER_API_KEY in .env")

    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=api_key,
        base_url=base_url,
    )

# --- Load Vectorstores ---
def load_vectorstore(collection_name: str):
    """Load existing vectorstore."""
    db_path = VECTOR_DB_PATH / collection_name
    embeddings = get_embedding_function()

    if not db_path.exists():
        raise FileNotFoundError(f"❌ Vectorstore not found: {db_path}")

    print(f"📂 Loaded vectorstore: {collection_name}")
    return Chroma(
        persist_directory=str(db_path),
        embedding_function=embeddings,
        collection_name=collection_name,
    )

# --- Core RAG Matching Logic ---
def match_project_to_employees(top_n=5):
    """Retrieve top N employees semantically similar to the project requirements."""
    print("🔍 Starting RAG-based employee matching...")

    # Load both vectorstores
    project_store = load_vectorstore("project_index")
    employee_store = load_vectorstore("employee_index")

    # Get project embedding
    project_docs = project_store.get(include=["documents", "metadatas"])
    project_text = project_docs["documents"][0]
    print(f"🧠 Project context loaded: {project_text[:100]}...")

    # Perform similarity search
    results = employee_store.similarity_search_with_score(project_text, k=top_n)

    matches = []
    for doc, score in results:
        metadata = doc.metadata or {}
        match = {
            "employee_id": metadata.get("id", "N/A"),
            "name": doc.page_content.split(",")[0].replace("Name:", "").strip(),
            "email": metadata.get("email", "N/A"),
            "similarity_score": round(float(score), 4)
        }
        matches.append(match)

    # Save output
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=4)

    print(f"✅ Top {top_n} semantic matches saved to {OUTPUT_PATH}")
    for m in matches:
        print(f" - {m['name']} ({m['email']}) | score: {m['similarity_score']}")

if __name__ == "__main__":
    match_project_to_employees(top_n=5)
