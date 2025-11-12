import os
import json
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parents[1]
VECTOR_DB_PATH = BASE_DIR / "data" / "vectorstores"
VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

# --- Embedding Setup ---
def get_embedding_function():
    """Initialize embedding model using OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        raise ValueError("❌ Missing OPENROUTER_API_KEY in .env")

    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=api_key,
        base_url=base_url,
    )

# --- Vectorstore Creation ---
def create_vectorstore(json_path: Path, collection_name: str):
    """Create and save vectorstore for given dataset (employees or projects)."""
    if not json_path.exists():
        raise FileNotFoundError(f"❌ File not found: {json_path}")

    # Load JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to text chunks for embedding
    documents = []
    metadatas = []

    if isinstance(data, list):  # employees.json
        for emp in data:
            text = f"Name: {emp.get('name')}, Role: {emp.get('role')}, Skills: {', '.join(emp.get('skills', []))}"
            documents.append(text)
            metadatas.append({"id": emp.get("employee_id"), "email": emp.get("email")})
    elif isinstance(data, dict):  # project analysis file
        text = f"Project: {data.get('project_name')}, Summary: {data.get('summary')}, Skills: {', '.join(data.get('required_skills', []))}"
        documents.append(text)
        metadatas.append({"project": data.get("project_name")})
    else:
        raise ValueError("❌ Unsupported data format for vectorstore creation.")

    # Initialize Chroma vectorstore
    embeddings = get_embedding_function()
    db_path = VECTOR_DB_PATH / collection_name

    vectorstore = Chroma.from_texts(
        texts=documents,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=collection_name,
        persist_directory=str(db_path),
    )

    print(f"✅ Vectorstore created successfully: {collection_name} → {db_path}")
    return vectorstore


def load_vectorstore(collection_name: str):
    """Load an existing Chroma vectorstore."""
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


if __name__ == "__main__":
    # Example usage (run once to create embeddings)
    EMP_PATH = BASE_DIR / "data" / "employees" / "employees.json"
    PROJ_PATH = BASE_DIR / "data" / "projects" / "analysis_001.json"

    create_vectorstore(EMP_PATH, "employee_index")
    create_vectorstore(PROJ_PATH, "project_index")
