import os
import json
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ---------------------------------------------------------------------
# 1️⃣ Environment Setup
# ---------------------------------------------------------------------
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY missing in .env")

# ---------------------------------------------------------------------
# 2️⃣ Initialize OpenRouter LLM (Meta-Llama-3)
# ---------------------------------------------------------------------
llm = ChatOpenAI(
    model="meta-llama/llama-3-8b-instruct",
    temperature=0.2,
    max_tokens=800,
    api_key=api_key,
    base_url=base_url,
)

# ---------------------------------------------------------------------
# 3️⃣ Core Analyzer Agent Logic
# ---------------------------------------------------------------------
def analyze_project(project_file_path: str) -> dict:
    """
    Reads a project requirement file and extracts structured info using the LLM.
    Returns a clean Python dictionary parsed from valid JSON.
    """

    # Ensure file exists
    if not os.path.exists(project_file_path):
        raise FileNotFoundError(f"❌ File not found: {project_file_path}")

    # Read project content
    with open(project_file_path, "r", encoding="utf-8") as f:
        project_text = f.read()

    # Build messages for LLM
    system_prompt = SystemMessage(content=(
        "You are an expert software project analyst. "
        "Your goal is to extract structured project details. "
        "Respond ONLY with valid JSON. "
        "Do not include explanations, text, or markdown code fences. "
        "The JSON must contain exactly these keys: "
        "project_name, summary, required_roles, required_skills, and domain."
    ))

    human_prompt = HumanMessage(content=f"Project requirement:\n{project_text}")

    # Send to LLM
    response = llm.invoke([system_prompt, human_prompt])
    raw_output = response.content.strip()

    # -----------------------------------------------------------------
    # 🧹 Cleanup Step: remove markdown/code fences and extract JSON
    # -----------------------------------------------------------------
    cleaned = raw_output
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # Try extracting JSON between braces if extra text exists
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    # -----------------------------------------------------------------
    # 🧩 Parse into Python dictionary
    # -----------------------------------------------------------------
    try:
        # try to load JSON normally
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Auto-fix truncated JSON if needed
        if not cleaned.endswith("}"):
            cleaned = cleaned + "}"
        try:
            result = json.loads(cleaned)
        except Exception:
            result = {"raw_response": raw_output}
    except Exception:
        result = {"raw_response": raw_output}

    return result


# ---------------------------------------------------------------------
# 4️⃣ Helper: Save JSON Analysis Output
# ---------------------------------------------------------------------
def save_analysis(project_id: str, analysis_data: dict):
    """
    Saves analysis output to data/projects/analysis_<project_id>.json
    """
    os.makedirs("data/projects", exist_ok=True)

    output_path = os.path.join("data", "projects", f"analysis_{project_id}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=4)

    print(f"✅ Analysis saved to {output_path}")


# ---------------------------------------------------------------------
# 5️⃣ Test Run (Optional)
# ---------------------------------------------------------------------
def main():
    test_file = "data/projects/project_001.txt"
    analysis = analyze_project(test_file)
    if isinstance(analysis, dict):
        save_analysis("001", analysis)
        print("✅ Analyzer completed.")
        return analysis
    else:
        print("⚠️ Analyzer result invalid.")
        return None

if __name__ == "__main__":
    main()

