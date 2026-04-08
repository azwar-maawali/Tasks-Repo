import subprocess
import platform
import json
import yagmail
from datetime import datetime

# ── Network Configuration ─────────────────────────────────
NETWORK_PREFIX = "192.168.100"   # Change to your network
START_IP       = 1
END_IP         = 25           # Adjust range as needed

# ── Email Configuration ───────────────────────────────────
SENDER_EMAIL   = "azalmawal@gmail.com"
APP_PASSWORD   = "App_password"
RECEIVER_EMAIL = "alazwaralmawali77@gmail.com"

# ── Report File ───────────────────────────────────────────
REPORT_FILE    = "/Users/alazwaralmaawali/Desktop/Python/Tasks-Repo/DAY 7/network_report.json"

# ── Ping Function ─────────────────────────────────────────
def ping(ip):
    system = platform.system()
    if system == "Windows":
        command = ["ping", "-n", "1", "-w", "1000", ip]
    else:
        command = ["ping", "-c", "1", "-W", "1", ip]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

# ── Scan Network ──────────────────────────────────────────
def scan_network():
    print(f"Scanning network {NETWORK_PREFIX}.{START_IP} - {NETWORK_PREFIX}.{END_IP}...")
    results = []

    for i in range(START_IP, END_IP + 1):
        ip     = f"{NETWORK_PREFIX}.{i}"
        status = "UP" if ping(ip) else "DOWN"
        print(f"  {ip} → {status}")
        results.append({"ip": ip, "status": status})

    return results

# ── Save Report ───────────────────────────────────────────
def save_report(results):
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_scanned": len(results),
        "total_up":      sum(1 for r in results if r["status"] == "UP"),
        "total_down":    sum(1 for r in results if r["status"] == "DOWN"),
        "devices":       results
    }

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=4)

    print(f"Report saved to {REPORT_FILE}")
    return report

# ── Send Email ────────────────────────────────────────────
def send_email(report):
    subject  = f"Network Scan Report - {report['timestamp']}"
    contents = [
        f"Network Scan completed at {report['timestamp']}",
        f"Total Scanned : {report['total_scanned']}",
        f"Total UP      : {report['total_up']}",
        f"Total DOWN    : {report['total_down']}",
        f"\nFull report attached.",
        REPORT_FILE
    ]

    try:
        print("Sending email report...")
        yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)
        yag.send(to=RECEIVER_EMAIL, subject=subject, contents=contents)
        print(f"Email sent successfully to {RECEIVER_EMAIL}")

    except Exception as e:
        print(f"Error sending email: {e}")

# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    results = scan_network()
    report  = save_report(results)
    send_email(report)