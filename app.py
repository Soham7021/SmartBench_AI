import streamlit as st
import os
import json
from pathlib import Path
from agents.graph_agent import workflow
from agents.notifier_agent import notify_all_shortlisted

# -------------------------------------------------------------------
# 📁 Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "data" / "projects"

PROJECT_FILE = PROJECTS_DIR / "project_001.txt"
ANALYSIS_FILE = PROJECTS_DIR / "analysis_001.json"
MATCHES_FILE = PROJECTS_DIR / "matches_001.json"
FINAL_MATCHES_FILE = PROJECTS_DIR / "final_matches.json"

# -------------------------------------------------------------------
# 🧹 Utility: Clear old files
# -------------------------------------------------------------------
def clear_old_files():
    """Remove old matches and selections before starting a new workflow."""
    for path in [MATCHES_FILE, FINAL_MATCHES_FILE]:
        if path.exists():
            path.unlink()
            print(f"🧹 Cleared old file: {path.name}")
    # Recreate an empty valid JSON file for safety
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    with open(FINAL_MATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# -------------------------------------------------------------------
# 🎨 Page Setup
# -------------------------------------------------------------------
st.set_page_config(page_title="SmartBench HR System", layout="wide")
st.title("🤖 SmartBench — AI-Powered Bench Allocation System")

st.markdown("""
Welcome to **SmartBench**, your intelligent bench management system.

It helps HR teams to:
1️⃣ Analyze project requirements  
2️⃣ Match relevant employees  
3️⃣ Select who to notify  
4️⃣ Send emails automatically 💌
""")

# -------------------------------------------------------------------
# 📤 Upload or Paste Section
# -------------------------------------------------------------------
uploaded_file = st.file_uploader("📁 Upload Project Requirement (.txt)", type=["txt"])
project_text = st.text_area("✍️ Or paste your project requirement manually:")

if uploaded_file:
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    with open(PROJECT_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File uploaded successfully: {uploaded_file.name}")

elif project_text.strip():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    with open(PROJECT_FILE, "w", encoding="utf-8") as f:
        f.write(project_text)
    st.success("✅ Project text saved successfully.")

# -------------------------------------------------------------------
# 🚀 Run Workflow
# -------------------------------------------------------------------
if st.button("🚀 Start SmartBench Workflow"):
    if not PROJECT_FILE.exists():
        st.error("❌ Please upload or enter a project description first.")
    else:
        clear_old_files()
        with st.spinner("Running full SmartBench pipeline..."):
            workflow.invoke({"messages": [{"role": "user", "content": "Start SmartBench workflow"}]})
        st.success("🎉 Workflow completed successfully! Employees matched below.")

# -------------------------------------------------------------------
# 👩‍💻 Display Matches (Safe Loading)
# -------------------------------------------------------------------
if MATCHES_FILE.exists() and MATCHES_FILE.stat().st_size > 0:
    try:
        with open(MATCHES_FILE, "r", encoding="utf-8") as f:
            matches = json.load(f)
    except json.JSONDecodeError:
        st.error("⚠️ Error reading matches file. Please re-run workflow.")
        matches = []

    if matches:
        st.subheader("👩‍💻 Matched Employees for this Project")
        st.markdown("Select the employees you want to notify via email:")

        selected = []
        for emp in matches:
            with st.expander(f"{emp['name']} — {emp['role']} ({emp['fit_score']}%)", expanded=False):
                st.json(emp)
            if st.checkbox(f"Select {emp['name']} ({emp['role']})", key=emp["employee_id"]):
                selected.append(emp)

        if st.button("💾 Save Selected Employees"):
            with open(FINAL_MATCHES_FILE, "w", encoding="utf-8") as f:
                json.dump(selected, f, indent=4)
            st.success(f"✅ Saved {len(selected)} selected employees to final_matches.json")

# -------------------------------------------------------------------
# 📧 Send Emails Section (Safe + Independent)
# -------------------------------------------------------------------
if FINAL_MATCHES_FILE.exists() and FINAL_MATCHES_FILE.stat().st_size > 0:
    try:
        with open(FINAL_MATCHES_FILE, "r", encoding="utf-8") as f:
            final_selected = json.load(f)
    except json.JSONDecodeError:
        st.warning("⚠️ final_matches.json is empty or invalid, resetting it.")
        final_selected = []

    if final_selected:
        st.subheader("📨 Ready to Send Emails")
        st.markdown(f"Total **{len(final_selected)}** employees selected for notification:")

        # ✅ Show a table summary
        st.table([{k: v for k, v in emp.items() if k in ["name", "role", "email", "fit_score"]} for emp in final_selected])

        if st.button("📤 Send Emails Now"):
            with st.spinner("Sending emails..."):
                notify_all_shortlisted()
            st.success("✅ Emails sent successfully to all selected employees!")

            # 🧹 Optional: Clear selections after sending
            with open(FINAL_MATCHES_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            st.info("🧹 Final matches cleared after email dispatch.")
    else:
        st.warning("⚠️ No employees selected yet.")
else:
    st.info("💡 Run workflow and select employees to enable email sending.")
