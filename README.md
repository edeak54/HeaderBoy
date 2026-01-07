**HeaderBoy** is an automated, web-based security header auditing platform. It transforms the powerful `shcheck` engine into a full-scale monitoring dashboard, allowing security teams to manage batch scans, track progress in real-time, and export compliance-ready reports.

### ✨ Advanced Features

🚀 **Flask Web Dashboard:** A clean UI to manage scans without touching the terminal.

🔄 **Smart Threading:** Background scan execution with a `threading.Lock` to prevent process collision.

🛑 **Force Stop Integration:** Ability to terminate active subprocesses safely via the UI.

📅 **Automated Scheduling:** Built-in auto-scan intervals for continuous infrastructure monitoring.

📊 **Excel Integration:** Seamlessly import target lists and export results via Pandas.

🛰️ **Live Progress Tracking:** Real-time JSON API endpoints to monitor scan status (`/scan_progress`).


### 🛠️ Technical Stack

* **Backend:** Python, Flask
* **Concurrency:** Threading (with daemon support)
* **Data Handling:** Pandas, Openpyxl (Excel processing)
* **Process Management:** Subprocess (Subprocess management with termination signals)
* **Frontend:** HTML/Jinja2 (Dashboard interface)

### 📋 Usage

1. **Initialize:** `python app.py`
2. **Access:** Open `http://127.0.0.1:5000` in your browser.
3. **Scan:** Upload an `.xlsx` file of domains and hit **Run Scan**.
4. **Monitor:** Watch live progress and export your `scan_results.xlsx` once complete.

---

## 💼 Upwork Portfolio Description (The "Pro" Version)

**Title:** Full-Stack Security Automation Dashboard (Python/Flask)
**Role:** Full-Stack Security Developer

**The Project:**
I developed a comprehensive security header auditing suite that automates the identification of missing security configurations (HSTS, CSP, X-Frame-Options) across large-scale domain lists.

**Key Accomplishments:**
⚙️ **Concurrency & Locking:** Implemented a thread-safe scanning engine that handles background tasks without UI freezing.
🔌 **API-First Design:** Built JSON endpoints to provide live scanning updates to the frontend.
📁 **Enterprise Data Handling:** Built a robust import/export system using Pandas to handle bulk Excel data.
🛡️ **Subprocess Control:** Integrated low-level system calls to manage and terminate external security tools safely via a web interface.

**Deliverables:**

* Full Flask Source Code (Modular & Documented).
* Threading & Process Management Logic.
* Excel-to-UI Data Pipeline.

---

## 🎯 Profile 1 & 2 Skills Update

Since you used **Flask**, **Threading**, and **Subprocess**, you need to add these tags to your Upwork profiles:

* **Profile 1 (Security Engineer):** Add `Vulnerability Management`, `Security Dashboards`, and `DevSecOps`.
* **Profile 2 (Scripting/Automation):** Add `Flask`, `Web Application`, `Concurrent Programming`, and `Pandas`.

**Would you like me to create a "Project Catalog" description for this? (This is the feature where clients can buy this specific dashboard from you for a fixed price).**
