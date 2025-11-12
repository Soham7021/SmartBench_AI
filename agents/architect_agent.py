import os
import json
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
# 2️⃣ Initialize LLM via OpenRouter
# ---------------------------------------------------------------------
llm = ChatOpenAI(
    model="meta-llama/llama-3-8b-instruct",
    temperature=0.25,
    max_tokens=1000,
    api_key=api_key,
    base_url=base_url,
)

# ---------------------------------------------------------------------
# 3️⃣ Core Architect Agent Logic
# ---------------------------------------------------------------------
def design_architecture(analysis_file_path: str) -> dict:
    """
    Reads analyzed project details from JSON and generates a
    technical architecture plan with recommended technologies and modules.
    """

    # Ensure input file exists
    if not os.path.exists(analysis_file_path):
        raise FileNotFoundError(f"❌ File not found: {analysis_file_path}")

    # Load analysis JSON
    with open(analysis_file_path, "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    # Convert to string for LLM context
    project_context = json.dumps(analysis_data, indent=2)

    # -----------------------------------------------------------------
    # 3A️⃣ Build prompts
    # -----------------------------------------------------------------
    system_prompt = SystemMessage(content=(
        "You are a senior software architect. "
        "Given structured project details, design a full technical architecture. "
        "Respond ONLY with valid JSON. No text outside JSON or markdown fences. "
        "Your JSON must include the following keys:\n"
        "architecture (frontend, backend, database, cloud), "
        "recommended_stack (libraries, frameworks), "
        "modules (major functional modules), and "
        "data_flow (high-level explanation)."
    ))

    human_prompt = HumanMessage(content=f"Project details:\n{project_context}")

    # -----------------------------------------------------------------
    # 3B️⃣ Generate response
    # -----------------------------------------------------------------
    response = llm.invoke([system_prompt, human_prompt])
    raw_output = response.content.strip()

    # Clean output (remove ```json fences if any)
    cleaned = raw_output.replace("```json", "").replace("```", "").strip()

    # Attempt to parse JSON
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Auto-fix truncated JSON if needed
        if not cleaned.endswith("}"):
            cleaned += "}"
        try:
            result = json.loads(cleaned)
        except Exception:
            result = {"raw_response": raw_output}
    except Exception:
        result = {"raw_response": raw_output}

    return result


# ---------------------------------------------------------------------
# 4️⃣ Save Architecture Plan
# ---------------------------------------------------------------------
def save_architecture(project_id: str, architecture_data: dict):
    """
    Saves the generated architecture JSON to data/projects/architecture_<project_id>.json
    """
    os.makedirs("data/projects", exist_ok=True)

    output_path = os.path.join("data", "projects", f"architecture_{project_id}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(architecture_data, f, indent=4)

    print(f"✅ Architecture saved to {output_path}")


# ---------------------------------------------------------------------
# 5️⃣ Test Run (Optional)
# ---------------------------------------------------------------------
def main():
    input_file = "data/projects/analysis_001.json"
    architecture_plan = design_architecture(input_file)
    if isinstance(architecture_plan, dict):
        save_architecture("001", architecture_plan)
        print("✅ Architect completed.")
        return architecture_plan
    else:
        print("⚠️ Architect result invalid.")
        return None

if __name__ == "__main__":
    main()

