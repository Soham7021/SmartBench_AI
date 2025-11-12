import json
import os
from difflib import SequenceMatcher
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ANALYSIS_PATH = BASE_DIR / "data" / "projects" / "analysis_001.json"
EMPLOYEE_DATA_PATH = BASE_DIR / "data" / "employees" / "employees.json"
OUTPUT_PATH = BASE_DIR / "data" / "projects" / "matches_001.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def calculate_fit_score(required_skills, employee_skills):
    matches = 0
    for req_skill in required_skills:
        for emp_skill in employee_skills:
            if calculate_similarity(req_skill, emp_skill) > 0.6:
                matches += 1
                break
    return int((matches / len(required_skills)) * 100)

def match_employees(project_data, employees):
    required_skills = project_data.get("required_skills", [])
    required_roles = [r.lower() for r in project_data.get("required_roles", [])]
    matches = []

    for emp in employees:
        # Skip employees whose role isn't part of required project roles
        if emp["role"].lower() not in required_roles:
            continue

        # Calculate similarity score
        role_match = any(
            calculate_similarity(emp["role"], role) > 0.6 for role in required_roles
        )
        skill_score = calculate_fit_score(required_skills, emp["skills"])
        overall_score = int((skill_score * 0.7) + (role_match * 30))

        matches.append({
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "role": emp["role"],
            "email": emp["email"],
            "skills": emp["skills"],
            "fit_score": overall_score
        })

    # Sort by fit_score descending
    matches = sorted(matches, key=lambda x: x["fit_score"], reverse=True)

    print(f"✅ Shortlisted {len(matches)} employees for required project roles.")
    return matches

# ✅ Just added this clean main()
def main():
    """Entry point for Matcher Agent."""
    if not PROJECT_ANALYSIS_PATH.exists() or not EMPLOYEE_DATA_PATH.exists():
        print("❌ Missing required data files.")
        return

    project_data = load_json(PROJECT_ANALYSIS_PATH)
    employees = load_json(EMPLOYEE_DATA_PATH)
    matches = match_employees(project_data, employees)

    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=4)

    print(f"✅ Matches saved to {OUTPUT_PATH}")
    print(json.dumps(matches[:5], indent=4))
    return matches

if __name__ == "__main__":
    main()
