import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime

# Import agents
from agents.analyzer_agent import analyze_project, save_analysis
from agents.architect_agent import design_architecture, save_architecture
from agents.matcher_agent import main as run_matcher
from agents.notifier_agent import notify_all_shortlisted

# -------------------------------------------------------------------
# 📁 Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "data" / "projects"

PROJECT_FILE = PROJECTS_DIR / "project_001.txt"
ANALYSIS_FILE = PROJECTS_DIR / "analysis_001.json"
ARCH_FILE = PROJECTS_DIR / "architecture_001.json"
MATCHES_FILE = PROJECTS_DIR / "matches_001.json"
FINAL_MATCHES_FILE = PROJECTS_DIR / "final_matches.json"

# -------------------------------------------------------------------
# 🧹 Utility: Clear old files
# -------------------------------------------------------------------
def clear_old_files():
    """Remove old files before new workflow"""
    for path in [ANALYSIS_FILE, ARCH_FILE, MATCHES_FILE, FINAL_MATCHES_FILE]:
        if path.exists():
            path.unlink()
            print(f"🧹 Cleared old file: {path.name}")
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    with open(FINAL_MATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# -------------------------------------------------------------------
# ✨ Pretty Architecture Display
# -------------------------------------------------------------------
def display_architecture(architecture: dict):
    st.markdown("""
    <div class="section-header">
        <h2>🧩 System Architecture Overview</h2>
    </div>
    """, unsafe_allow_html=True)

    # show version/timestamp
    if ARCH_FILE.exists():
        ts = datetime.fromtimestamp(ARCH_FILE.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        st.markdown(f"""
        <div class="timestamp-badge">
            <span>🕒 Last Updated: {ts}</span>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    def render_content(content):
        """Convert dict/list content into nice readable text."""
        if isinstance(content, dict):
            items = "".join([f"<div class='content-item'><span class='label'>{k.capitalize()}:</span> <span class='value'>{v}</span></div>" for k, v in content.items()])
            return f"<div class='content-wrapper'>{items}</div>"
        elif isinstance(content, list):
            return "<ul class='custom-list'>" + "".join([f"<li>{item}</li>" for item in content]) + "</ul>"
        else:
            return f"<span class='content-text'>{str(content)}</span>"

    with col1:
        frontend = architecture.get("architecture", {}).get("frontend", "N/A")
        backend = architecture.get("architecture", {}).get("backend", "N/A")
        st.markdown(f"""
        <div class="arch-card frontend-card">
            <div class="card-icon">💻</div>
            <h3>Frontend</h3>
            <div class="card-content">{render_content(frontend)}</div>
        </div>
        <div class="arch-card backend-card">
            <div class="card-icon">⚙️</div>
            <h3>Backend</h3>
            <div class="card-content">{render_content(backend)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        database = architecture.get("architecture", {}).get("database", "N/A")
        cloud = architecture.get("architecture", {}).get("cloud", "N/A")
        st.markdown(f"""
        <div class="arch-card database-card">
            <div class="card-icon">🗄️</div>
            <h3>Database</h3>
            <div class="card-content">{render_content(database)}</div>
        </div>
        <div class="arch-card cloud-card">
            <div class="card-icon">☁️</div>
            <h3>Cloud Infrastructure</h3>
            <div class="card-content">{render_content(cloud)}</div>
        </div>
        """, unsafe_allow_html=True)

    rec_stack = architecture.get("recommended_stack", [])
    if rec_stack:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>🧰 Recommended Tech Stack</h3>", unsafe_allow_html=True)
        tech_badges = " ".join([f"<span class='tech-badge'>{tech}</span>" for tech in rec_stack])
        st.markdown(f"<div class='tech-stack-container'>{tech_badges}</div>", unsafe_allow_html=True)

    modules = architecture.get("modules", [])
    if modules:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>🧱 Major System Modules</h3>", unsafe_allow_html=True)
        for mod in modules:
            if isinstance(mod, dict):
                st.markdown(f"""
                <div class='module-item'>
                    <span class='module-name'>{mod.get('name', '')}</span>
                    <span class='module-desc'>{mod.get('description', '')}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='module-item'><span class='module-name'>{mod}</span></div>", unsafe_allow_html=True)

    data_flow = architecture.get("data_flow", {})
    desc = data_flow.get("description", "") if isinstance(data_flow, dict) else str(data_flow)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='data-flow-section'>
        <h3 class='subsection-title'>🔄 Data Flow</h3>
        <p class='data-flow-desc'>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🎨 Custom CSS Styling
# -------------------------------------------------------------------
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@600;700&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
    }
    
    .block-container {
        max-width: 1200px;
        padding: 2rem 3rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 0 auto;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
        color: #2d3748;
    }
    
    p, li, span, div {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        line-height: 1.8;
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: #2d3748;
        font-size: 1rem;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 2px dashed #667eea;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .section-header h2 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
    }
    
    /* Architecture Cards */
    .arch-card {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .arch-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.8) 100%);
    }
    
    .arch-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    .frontend-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .backend-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    }
    
    .database-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    }
    
    .cloud-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    }
    
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .arch-card h3 {
        color: #2d3748;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .card-content {
        color: #4a5568;
        line-height: 1.6;
    }
    
    .content-item {
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: rgba(255,255,255,0.5);
        border-radius: 5px;
    }
    
    .label {
        font-weight: 600;
        color: #2d3748;
    }
    
    .value {
        color: #4a5568;
    }
    
    /* Tech Stack */
    .tech-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .tech-stack-container {
        margin: 1rem 0;
    }
    
    /* Modules */
    .module-item {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .module-name {
        font-weight: 600;
        color: #2d3748;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .module-desc {
        color: #4a5568;
        font-size: 0.9rem;
    }
    
    /* Data Flow */
    .data-flow-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .data-flow-desc {
        color: #2d3748;
        font-size: 1rem;
        line-height: 1.8;
        margin: 0;
    }
    
    /* Section Divider */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    
    .subsection-title {
        color: #2d3748;
        font-size: 1.5rem;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    /* Timestamp Badge */
    .timestamp-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Employee Cards */
    .stExpander {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Success/Warning Messages */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid #17a2b8;
    }
    
    /* File Uploader */
    .uploadedFile {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Custom List */
    .custom-list {
        list-style: none;
        padding: 0;
    }
    
    .custom-list li {
        background: rgba(255,255,255,0.7);
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        border-left: 3px solid #667eea;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .feature-card, .arch-card, .module-item {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }
        
        .main-title {
            font-size: 2rem;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🎨 Page Setup
# -------------------------------------------------------------------
st.set_page_config(
    page_title="SmartBench HR System", 
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
load_custom_css()

# Header
st.markdown("""
<h1 class="main-title">🤖 SmartBench</h1>
<p class="subtitle">AI-Powered Intelligent Bench Allocation System</p>
""", unsafe_allow_html=True)

# Feature Cards
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Analyze Requirements</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🏗️</div>
        <div class="feature-title">Design Architecture</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">👥</div>
        <div class="feature-title">Match Employees</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📧</div>
        <div class="feature-title">Automated Notifications</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 📤 Upload or Paste Section
# -------------------------------------------------------------------
st.markdown("""
<div class="section-header">
    <h2>📁 Upload Project Requirements</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    uploaded_file = st.file_uploader("📁 Upload Project Requirement (.txt)", type=["txt"], label_visibility="collapsed")
    if uploaded_file:
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        with open(PROJECT_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File uploaded successfully: {uploaded_file.name}")

with col2:
    project_text = st.text_area("✍️ Or paste your project requirement manually:", height=150, label_visibility="collapsed", placeholder="Paste your project requirements here...")
    if project_text.strip():
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        with open(PROJECT_FILE, "w", encoding="utf-8") as f:
            f.write(project_text)
        st.success("✅ Project text saved successfully.")

# -------------------------------------------------------------------
# 🚀 Step 1: Analyze Project
# -------------------------------------------------------------------
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔍 Analyze Project", use_container_width=True):
        if not PROJECT_FILE.exists():
            st.error("❌ Please upload or enter a project description first.")
        else:
            clear_old_files()
            with st.spinner("Analyzing project requirements..."):
                result = analyze_project(str(PROJECT_FILE))
                save_analysis("001", result)
            st.success("🧠 Project analysis completed successfully!")
            st.balloons()

# -------------------------------------------------------------------
# 🏗️ Step 2: Generate Architecture
# -------------------------------------------------------------------
if ANALYSIS_FILE.exists():
    st.markdown("""
    <div class="section-header">
        <h2>🏗️ Architecture Design</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚙️ Generate Architecture Plan", use_container_width=True):
            with st.spinner("Designing system architecture..."):
                arch_data = design_architecture(str(ANALYSIS_FILE))
                save_architecture("001", arch_data)
            st.success("✅ Architecture plan generated!")
            st.balloons()

# -------------------------------------------------------------------
# 📘 Step 3: Review & Approve Architecture
# -------------------------------------------------------------------
if ARCH_FILE.exists():
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    with open(ARCH_FILE, "r", encoding="utf-8") as f:
        architecture = json.load(f)

    # 🎨 Display architecture
    display_architecture(architecture)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        approve = st.button("✅ Approve Architecture", use_container_width=True)
    with col2:
        regenerate = st.button("🔁 Re-generate Architecture", use_container_width=True)

    if regenerate:
        with st.spinner("🔄 Re-generating architecture..."):
            arch_data = design_architecture(str(ANALYSIS_FILE))
            save_architecture("001", arch_data)
        st.toast("🔃 Architecture regenerated — refreshing view...", icon="♻️")
        st.rerun()

# -------------------------------------------------------------------
# ⚙️ Step 4: Match Employees
# -------------------------------------------------------------------
if ARCH_FILE.exists() and "approve" in locals() and approve:
    st.markdown("""
    <div class="section-header">
        <h2>👩‍💻 Employee Matching</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Running employee matching..."):
        run_matcher()
    st.success("✅ Employees matched successfully!")
    st.balloons()

# -------------------------------------------------------------------
# 👩‍💻 Step 5: Display Matches & HR Selection
# -------------------------------------------------------------------
if MATCHES_FILE.exists() and MATCHES_FILE.stat().st_size > 0:
    try:
        with open(MATCHES_FILE, "r", encoding="utf-8") as f:
            matches = json.load(f)
    except json.JSONDecodeError:
        st.error("⚠️ Error reading matches file. Please re-run workflow.")
        matches = []

    if matches:
        st.markdown("""
        <div class="section-header">
            <h2>👥 Matched Employees</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #4a5568; font-size: 1.1rem; margin: 1rem 0;'>Select the employees you want to notify via email:</p>", unsafe_allow_html=True)

        selected = []
        for emp in matches:
            with st.expander(f"👤 {emp['name']} — {emp['role']} ({emp['fit_score']}%)", expanded=False):
                st.json(emp)
            if st.checkbox(f"Select {emp['name']} ({emp['role']})", key=emp["employee_id"]):
                selected.append(emp)

        if selected:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Save Selected Employees", use_container_width=True):
                    with open(FINAL_MATCHES_FILE, "w", encoding="utf-8") as f:
                        json.dump(selected, f, indent=4)
                    st.success(f"✅ Saved {len(selected)} selected employees to final_matches.json")

# -------------------------------------------------------------------
# ✉️ Step 6: Send Emails
# -------------------------------------------------------------------
if FINAL_MATCHES_FILE.exists() and FINAL_MATCHES_FILE.stat().st_size > 0:
    try:
        with open(FINAL_MATCHES_FILE, "r", encoding="utf-8") as f:
            final_selected = json.load(f)
    except json.JSONDecodeError:
        st.warning("⚠️ final_matches.json invalid, resetting it.")
        final_selected = []

    if final_selected:
        st.markdown("""
        <div class="section-header">
            <h2>📨 Email Notification</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align: center; color: #4a5568; font-size: 1.1rem; margin: 1rem 0;'>Ready to notify <strong>{len(final_selected)}</strong> selected employees</p>", unsafe_allow_html=True)

        st.table([{k: v for k, v in emp.items() if k in ["name", "role", "email", "fit_score"]} for emp in final_selected])

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Send Emails Now", use_container_width=True):
                with st.spinner("Sending emails..."):
                    notify_all_shortlisted()
                st.success("✅ Emails sent successfully to all selected employees!")
                st.balloons()

                # 🧹 Clear final matches after sending
                with open(FINAL_MATCHES_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f)
                st.info("🧹 Final matches cleared after email dispatch.")
    else:
        st.warning("⚠️ No employees selected yet.")
else:
    st.info("💡 Complete the workflow steps above to enable email notifications.")