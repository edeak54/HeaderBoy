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
