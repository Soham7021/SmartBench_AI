import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# ------------------------------------------------------------
# 1️⃣ Load ENV
# ------------------------------------------------------------
load_dotenv()
g_api_key = os.getenv("GOOGLE_API_KEY")

if not g_api_key:
    raise ValueError("❌ GOOGLE_API_KEY missing in .env")

# ------------------------------------------------------------
# 2️⃣ Initialize Gemini 2.0 Flash
# ------------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=g_api_key,
    temperature=0.2,
    max_output_tokens=3000,
)

# ------------------------------------------------------------
# 3️⃣ Helper — ensure JSON output
# ------------------------------------------------------------
def _ask_llm(prompt: str) -> dict:
    """Ask LLM and ensure JSON is parsed safely."""
    response = llm.invoke([
        SystemMessage(content="You are Gemini. Follow instructions EXACTLY."),
        HumanMessage(content=prompt)
    ])

    raw = response.content.strip()
    cleaned = raw.replace("```json", "").replace("```", "")

    try:
        return json.loads(cleaned)
    except:
        print("⚠️ JSON parse failed. Returning raw output.")
        return {"raw_response": raw}

# ------------------------------------------------------------
# 4️⃣ Strict JSON Schema (important)
# ------------------------------------------------------------
ARCH_SCHEMA = """
{
  "architecture": {
    "frontend": "string",
    "backend": "string",
    "database": "string",
    "cloud": "string"
  },
  "recommended_stack": [
    "string"
  ],
  "modules": [
    {
      "name": "string",
      "description": "string"
    }
  ],
  "data_flow": {
    "description": "string"
  },
  "diagram_graphviz": "string"
}
"""

# ------------------------------------------------------------
# 5️⃣ Generate Architecture (first time)
# ------------------------------------------------------------
def design_architecture(analysis_file_path: str) -> dict:
    if not os.path.exists(analysis_file_path):
        raise FileNotFoundError(f"❌ Missing: {analysis_file_path}")

    analysis_data = json.loads(open(analysis_file_path, "r").read())
    project_context = json.dumps(analysis_data, indent=2)

    prompt = f"""
You are a senior enterprise solution architect.

Your task:
Generate a COMPLETE architecture using the following STRICT JSON schema:

SCHEMA:
{ARCH_SCHEMA}

RULES:
- Follow schema EXACTLY.
- "architecture" MUST be an OBJECT with frontend, backend, database, cloud.
- "recommended_stack" MUST be a LIST.
- "modules" MUST be a LIST of objects.
- "data_flow" MUST contain a single field "description".
- "diagram_graphviz" MUST be a VALID Graphviz DOT diagram.
- NO markdown, NO extra text.

DIAGRAM RULES:
- Generate a beautiful diagram of the architecture
- Use Nodes and edges
- use colours


Project Requirements:
{project_context}
"""

    return _ask_llm(prompt)

# ------------------------------------------------------------
# 6️⃣ Re-Generate Architecture With Feedback
# ------------------------------------------------------------
def redesign_architecture(analysis_file_path: str, feedback: str) -> dict:
    analysis_data = json.loads(open(analysis_file_path, "r").read())
    context = json.dumps(analysis_data, indent=2)

    prompt = f"""
You are a senior enterprise architect.

Re-generate the architecture STRICTLY following this schema:

SCHEMA:
{ARCH_SCHEMA}

User feedback that MUST be applied:
{feedback}

RULES:
- Follow the schema exactly.
- "architecture" MUST be an object with 4 fields.
- Use Nodes and edges to display the diagram instead of recatangular box
- Strictly Use colours to make architecutre more attractive
- "modules" MUST be a list of objects.
- "diagram_graphviz" MUST be valid DOT.
- Output JSON ONLY. No text outside the JSON.

Project details:
{context}
"""

    return _ask_llm(prompt)

# ------------------------------------------------------------
# 7️⃣ Save Architecture JSON
# ------------------------------------------------------------
def save_architecture(project_id: str, architecture_data: dict):
    os.makedirs("data/projects", exist_ok=True)
    path = f"data/projects/architecture_{project_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(architecture_data, f, indent=4)
    print(f"✅ Architecture saved → {path}")

# ------------------------------------------------------------
# Optional Test
# ------------------------------------------------------------
def main():
    result = design_architecture("data/projects/analysis_001.json")
    save_architecture("001", result)
    print("🚀 Architecture generation complete.")

if __name__ == "__main__":
    main()

