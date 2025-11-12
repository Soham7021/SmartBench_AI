import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path
from tabulate import tabulate  # ✅ For cleaner summary table

# ---------------------------------------------------------------------
# 1️⃣ Environment Setup
# ---------------------------------------------------------------------
load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECTS_DIR = BASE_DIR / "data" / "projects"

FINAL_MATCHES_PATH = PROJECTS_DIR / "final_matches.json"   # ✅ HR-approved list
MATCHES_PATH = PROJECTS_DIR / "matches_001.json"           # fallback if final not found

# ✅ Test Mode (no actual emails)
TEST_MODE = False

# ---------------------------------------------------------------------
# 2️⃣ Send Email Function
# ---------------------------------------------------------------------
def send_email_smtp(receiver_email: str, subject: str, body: str) -> bool:
    """Send an email using Gmail SMTP or simulate in test mode."""
    if TEST_MODE:
        print(f"[TEST MODE] 📧 Would send email to: {receiver_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}\n{'-'*70}")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"📩 Email sent successfully to {receiver_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {receiver_email}: {e}")
        return False

# ---------------------------------------------------------------------
# 3️⃣ Notify Logic
# ---------------------------------------------------------------------
def notify_all_shortlisted():
    """Notify all employees in final_matches.json (fallback: matches_001.json)."""
    file_to_read = FINAL_MATCHES_PATH if FINAL_MATCHES_PATH.exists() else MATCHES_PATH

    if not file_to_read.exists():
        print("❌ No matches or final selection file found.")
        return

    with open(file_to_read, "r", encoding="utf-8") as f:
        matches = json.load(f)

    if not matches:
        print("⚠️ No shortlisted employees found.")
        return

    print(f"📊 Preparing to notify {len(matches)} shortlisted employees from {file_to_read.name}...\n")

    summary = []

    for match in matches:
        name = match.get("name", "Candidate")
        email = match.get("email")
        role = match.get("role", "Employee")
        score = match.get("fit_score", 0)

        subject = "You're Shortlisted for a New Project!"
        body = (
            f"Dear {name},\n\n"
            f"Congratulations! 🎉\n\n"
            f"You have been shortlisted for an upcoming project that matches your skills as a {role}.\n"
            f"Your profile achieved a fit score of {score}/100.\n\n"
            f"Please reply to this email if you're available to take up this project.\n\n"
            f"Best regards,\nSmartBench HR System"
        )

        if email:
            success = send_email_smtp(email, subject, body)
            summary.append([name, role, email, f"{score}%", "✅ Sent" if success else "❌ Failed"])
        else:
            summary.append([name, role, "N/A", f"{score}%", "⚠️ No Email"])

    print("\n📋 Email Summary:")
    print(tabulate(summary, headers=["Name", "Role", "Email", "Fit Score", "Status"], tablefmt="grid"))
    print("\n✅ Notification process completed successfully.")

# ---------------------------------------------------------------------
# 4️⃣ Entry Point
# ---------------------------------------------------------------------
def main():
    """Entry point for Notifier Agent."""
    print("📨 Running Notifier Agent...")
    mode = "TEST MODE (No real emails sent)" if TEST_MODE else "LIVE MODE (Emails will be sent)"
    print(f"⚙️ Current Mode: {mode}\n")
    notify_all_shortlisted()
    print("\n✅ Notifier Agent completed successfully.")
    return "Notifier completed."

if __name__ == "__main__":
    main()
