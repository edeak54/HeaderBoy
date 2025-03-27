import os
import subprocess
import sys
import pandas as pd
import threading
import time
import json
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
INPUT_FILE = "current_input.xlsx"
RESULT_FILE = "scan_results.xlsx"
SCAN_INTERVAL = 3600  # Time in seconds (adjust as needed)
last_scan_timestamp = time.time()
scan_lock = threading.Lock()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_data():
    """Load scan results into a DataFrame."""
    if os.path.exists(RESULT_FILE):
        df = pd.read_excel(RESULT_FILE).fillna("")
        print("[DEBUG] Loaded Data:\n", df.head())  # Print the first few rows
        return df
    print("[DEBUG] scan_results.xlsx not found.")
    return pd.DataFrame()



def update_scan_status(status):
    """Update the scan status in a file."""
    with open("scan_status.txt", "w") as f:
        f.write(status)


def get_scan_status():
    """Read the scan status from a file."""
    try:
        with open("scan_status.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "completed"


def get_remaining_time():
    """Calculate time remaining until the next scan."""
    elapsed = time.time() - last_scan_timestamp
    return max(0, SCAN_INTERVAL - int(elapsed))


def run_scan_script():
    """Run security headers scan while preventing duplicate scans."""
    global last_scan_timestamp, force_stop
    force_stop = False  # Reset force stop flag

    if scan_lock.locked():
        print("[Scan] Skipping: Another scan is already running.")
        return

    with scan_lock:
        last_scan_timestamp = time.time()  # Update last scan timestamp
        update_scan_status("scanning")
        print("[Scan] Running scan...")

        if os.path.exists(INPUT_FILE):
            process = subprocess.Popen([sys.executable, "main.py", INPUT_FILE])
            
            # Loop to check if force stop is requested
            while process.poll() is None:  # Process is still running
                if force_stop:
                    process.terminate()  # Forcefully stop the scan
                    print("[Scan] Force stop triggered. Scan terminated.")
                    update_scan_status("stopped")
                    return
                time.sleep(1)  # Check every second

        else:
            print("[Scan] No input file found. Skipping.")

        update_scan_status("completed")
        print("[Scan] Scan completed.")

@app.route("/scan_progress")
def scan_progress():
    """Return current scanning progress."""
    try:
        with open("scan_progress.txt", "r") as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"current_url": "N/A", "scanned": 0, "total": 0})


def auto_scan():
    """Automatically trigger scans at set intervals."""
    while True:
        time.sleep(SCAN_INTERVAL)
        if not scan_lock.locked():
            print("[Auto-Scan] Running scheduled security headers check...")
            run_scan_script()
        else:
            print("[Auto-Scan] Skipped: Another scan is already running.")


# Start auto-scan thread
threading.Thread(target=auto_scan, daemon=True).start()


@app.route("/")
def index():
    """Render the main dashboard."""
    df = load_data()
    return render_template(
        "index.html",
        data=df.to_dict(orient="records"),
        headers=df.columns,
        total_results=len(df),
        last_scanned=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_scan_timestamp)),
        scan_interval=SCAN_INTERVAL,
        next_scan_in=get_remaining_time(),
        is_scanning=get_scan_status() == "scanning",
    )


@app.route("/run_scan", methods=["POST"])
def run_scan():
    """Manually trigger a scan."""
    if scan_lock.locked():
        return jsonify({"status": "already_running"})

    threading.Thread(target=run_scan_script, daemon=True).start()
    return jsonify({"status": "started"})

# Added global force stop flag
force_stop = False  

@app.route("/force_stop", methods=["POST"])
def force_stop_scan():
    """Force stop the current scan."""
    global force_stop
    force_stop = True  # Set flag to stop scan
    return jsonify({"status": "stopping"})
PROGRESS_FILE = "scan_progress.txt"
def update_progress(current_url, scanned, total):
    """Update progress in a file."""
    progress_data = {
        "current_url": current_url,
        "scanned": scanned,
        "total": total
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress_data, f)

def scan_urls(url_list):
    """Example scan function that simulates URL scanning."""
    total_urls = len(url_list)
    for index, url in enumerate(url_list, start=1):
        update_progress(url, index, total_urls)  # Update progress file
        time.sleep(2)  # Simulate scanning delay

@app.route("/import", methods=["POST"])
def import_file():
    """Handle file upload and trigger a new scan."""
    global last_scan_timestamp

    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "No file uploaded."})

    temp_file_path = os.path.join(UPLOAD_FOLDER, "temp_input.xlsx")
    file.save(temp_file_path)
    print("[Import] File uploaded.")

    while scan_lock.locked():
        print("[Import] Waiting for scan to finish before replacing input file...")
        time.sleep(2)

    os.replace(temp_file_path, INPUT_FILE)
    print("[Import] New file replaced.")

    last_scan_timestamp = time.time()  # Update last scanned time

    threading.Thread(target=run_scan_script, daemon=True).start()

    return jsonify({"status": "imported"})


@app.route("/export")
def export_file():
    """Export the scan results."""
    if os.path.exists(RESULT_FILE):
        return send_file(RESULT_FILE, as_attachment=True)
    return jsonify({"status": "error", "message": "No results available."})


@app.route("/scan_status")
def scan_status():
    """Return scanning status for frontend."""
    return jsonify({"status": get_scan_status()})


if __name__ == "__main__":
    app.run(debug=True)
