import re
import csv
import json
import os
from collections import Counter
from datetime import datetime

# ── File paths ──────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
LOG_FILE    = os.path.join(BASE_DIR, "firewall.log")
CSV_FILE    = os.path.join(BASE_DIR, "output.csv")
JSON_FILE   = os.path.join(BASE_DIR, "output.json")
THREAT_FILE = os.path.join(BASE_DIR, "threats.txt")

# ── Storage ──────────────────────────────────────────────
valid_entries   = []
total_processed = 0
malformed       = 0

# ── Regex pattern for a valid log line ───────────────────
pattern = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<action>ACCEPT|DROP)\s+"
    r"(?P<protocol>TCP|UDP|ICMP)\s+"
    r"SRC=(?P<source_ip>\S+)\s+SPT=(?P<source_port>\d+)\s+"
    r"DST=(?P<destination_ip>\S+)\s+DPT=(?P<destination_port>\d+)\s+"
    r"LEN=(?P<packet_size>\d+)"
)

# ── Step 1: Read and parse firewall.log ───────────────────
with open(LOG_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        total_processed += 1
        match = pattern.match(line)

        if match:
            valid_entries.append(match.groupdict())
        else:
            malformed += 1

# ── Step 2: Analysis ──────────────────────────────────────

# Count ACCEPT vs DROP
action_counts = Counter(e["action"] for e in valid_entries)

# Top 3 destination ports
port_counts = Counter(e["destination_port"] for e in valid_entries)
top3_ports  = port_counts.most_common(3)

# Suspicious IPs (3+ appearances)
ip_counts      = Counter(e["source_ip"] for e in valid_entries)
suspicious_ips = {ip: count for ip, count in ip_counts.items() if count >= 3}

# ── Step 3: Save output.csv ───────────────────────────────
with open(CSV_FILE, "w", newline="") as f:
    fieldnames = ["timestamp", "action", "protocol", "source_ip",
                  "source_port", "destination_ip", "destination_port", "packet_size"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(valid_entries)

# ── Step 4: Save output.json ──────────────────────────────
with open(JSON_FILE, "w") as f:
    json.dump(valid_entries, f, indent=4)

# ── Step 5: Save threats.txt ──────────────────────────────
with open(THREAT_FILE, "w") as f:
    f.write(f"THREAT REPORT - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 48 + "\n")
    f.write("Suspicious IPs (3+ log appearances):\n")
    for ip, count in suspicious_ips.items():
        f.write(f"  IP: {ip} | Occurrences: {count}\n")

# ── Step 6: Terminal Report ───────────────────────────────
print("=" * 60)
print("  FIREWALL LOG ANALYSIS REPORT")
print("=" * 60)
print(f"Total entries processed  : {total_processed}")
print(f"Valid entries parsed     : {len(valid_entries)}")
print(f"Malformed entries skipped: {malformed}")

print("\n--- Action Summary ---")
print(f"  ACCEPT : {action_counts.get('ACCEPT', 0)}")
print(f"  DROP   : {action_counts.get('DROP', 0)}")

print("\n--- Top 3 Targeted Destination Ports ---")
for i, (port, hits) in enumerate(top3_ports, 1):
    print(f"  {i}. Port {port} — {hits} hits")

print("\n--- Suspicious Source IPs (3+ appearances) ---")
for ip, count in suspicious_ips.items():
    print(f"  {ip} — {count} occurrences")

print("\nOutput saved:")
print(f"  {CSV_FILE}")
print(f"  {JSON_FILE}")
print(f"  {THREAT_FILE}")
print("=" * 60)