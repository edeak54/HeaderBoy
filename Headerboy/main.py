import pandas as pd
import subprocess
import re
import sys
import json

def update_progress(current_url, scanned, total):
    """Update progress in a file."""
    progress_data = {
        "current_url": current_url,
        "scanned": scanned,
        "total": total
    }
    with open("scan_progress.txt", "w") as f:
        json.dump(progress_data, f)

def remove_ansi_codes(text):
    """Remove ANSI color codes from shcheck.py output."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_headers_using_shcheck(url):
    """Run shcheck.py and return output, skipping slow URLs."""
    try:
        result = subprocess.run(
            [sys.executable, "shcheck/shcheck.py", url, "-d"],
            capture_output=True, text=True, timeout=15
        )
        return remove_ansi_codes(result.stdout)

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Skipping {url} (took too long)")
        return "TIMEOUT"

    except Exception as e:
        print(f"shcheck.py request failed for {url}: {e}")
        return ""

def get_set_cookie_headers(url):
    """Fetch Set-Cookie headers using curl -IL and check configuration."""
    try:
        result = subprocess.run(
            ["curl", "-IL", url], capture_output=True, text=True, timeout=10
        )
        headers = result.stdout.lower()  # Convert to lowercase for consistency

        match = re.findall(r'set-cookie:\s*(.*)', headers)

        if not match:
            return "MISSING", "-"  # No Set-Cookie header found

        set_cookie_value = "; ".join(match)  # Merge multiple Set-Cookie values

        misconfigured_reasons = []
        if "f5" in set_cookie_value:
            misconfigured_reasons.append("F5 Informational Disclosure")
        if "max-age" not in set_cookie_value:
            misconfigured_reasons.append("No Max-Age")
        if "secure" not in set_cookie_value:
            misconfigured_reasons.append("No Secure")
        if "httponly" not in set_cookie_value:
            misconfigured_reasons.append("No HttpOnly")
        if "domain" not in set_cookie_value:
            misconfigured_reasons.append("No Domain")

        if misconfigured_reasons:
            return "MSCONFIGURED", ", ".join(misconfigured_reasons)

        return "PRESENT", set_cookie_value  # Fully compliant

    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Set-Cookie check timed out"
    except Exception as e:
        return "ERROR", str(e)

def normalize_url(domain):
    """Ensure the URL has a scheme (http or https), preserving if already present."""
    if domain.startswith(("http://", "https://")):
        return domain
    return f"https://{domain}"  # Default to HTTPS if missing

def check_security_headers(domain):

    
    """Analyze security headers and handle timeouts properly."""
    url = normalize_url(domain)
    headers_text = get_headers_using_shcheck(url)

    if headers_text == "TIMEOUT":
        return [domain, url, "-", "Scan Timed Out", "-"]

    # If HTTPS fails, try HTTP (unless the original input was already HTTP)
    if not headers_text and url.startswith("https://"):
        url = f"http://{domain.replace('https://', '')}"
        headers_text = get_headers_using_shcheck(url)

    if headers_text == "TIMEOUT":
        return [domain, url, "-", "Scan Timed Out", "-"]

    if not headers_text:
        return [domain, url, "-", "All Headers Missing", "-"]

    present_headers = []
    missing_headers = []
    misconfigured_headers = {}

    headers_to_check = {
        "X-Frame-Options": ["SAMEORIGIN", "DENY"],
        "X-Content-Type-Options": ["nosniff"],
        "Strict-Transport-Security": ["max-age=31536000"],
        "Referrer-Policy": ["strict-origin-when-cross-origin"],
        "Content-Security-Policy": ["any"],
        "Permissions-Policy": ["any"]
    }

    for header, expected_values in headers_to_check.items():
        present_marker = f"[*] Header {header} is present!"
        insecure_marker = f"[!] Insecure header {header} is set!"
        missing_marker = f"[!] Missing security header: {header}"

        if present_marker in headers_text:
            present_headers.append(header)
            match = re.search(rf"\[\*\] Header {header} is present!\s*\(Value:\s*(.*?)\)", headers_text)
            actual_value = match.group(1).strip() if match else ""

            if expected_values != ["any"]:
                if header == "Strict-Transport-Security" and "max-age=31536000" not in actual_value:
                    misconfigured_headers[header] = actual_value
                elif header == "X-Frame-Options" and not any(opt in actual_value for opt in expected_values):
                    misconfigured_headers[header] = actual_value
                elif actual_value not in expected_values:
                    misconfigured_headers[header] = actual_value

        elif insecure_marker in headers_text:
            present_headers.append(header)
            match = re.search(rf"\[!\] Insecure header {header} is set!\s*\(Value:\s*(.*?)\)", headers_text)
            actual_value = match.group(1).strip() if match else "Unknown"
            misconfigured_headers[header] = actual_value

        elif missing_marker in headers_text:
            missing_headers.append(header)
        else:
            missing_headers.append(header)

    # 🔹 Check Set-Cookie using curl
    set_cookie_status, set_cookie_value = get_set_cookie_headers(url)

    # 🔹 Merge Set-Cookie with other headers
    if set_cookie_status == "PRESENT":
        present_headers.append("Set-Cookie")
    elif set_cookie_status == "MISSING":
        missing_headers.append("Set-Cookie")
    elif set_cookie_status == "MSCONFIGURED":
        misconfigured_headers["Set-Cookie"] = set_cookie_value

    return [
        domain,
        url,
        ", ".join(present_headers) if present_headers else "-",
        ", ".join(missing_headers) if missing_headers else "-",
        ", ".join([f"{h}: {v}" for h, v in misconfigured_headers.items()]) if misconfigured_headers else "-"
    ]

def process_excel(file_path):
    """Process an Excel file with a list of domains."""
    df = pd.read_excel(file_path)
    results = []
    total_domains = len(df)

    for index, domain in enumerate(df.iloc[:, 0], start=1):  # Assume first column contains domains
        # Update progress before scanning each domain
        update_progress(domain.strip(), index, total_domains)
        
        results.append(check_security_headers(domain.strip()))

    result_df = pd.DataFrame(results, columns=[
        "Domain", "Used URL", "Present Headers", "Missing Headers", "Misconfigured Headers"
    ])

    output_file = "scan_results.xlsx"
    result_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")

# Example usage
process_excel("current_input.xlsx")
