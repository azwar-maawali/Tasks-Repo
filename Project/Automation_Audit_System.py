import paramiko
from datetime import date
import os

# --- SSH Key Setup ---
key_path = os.path.expanduser("~/.ssh/id_rsa_paramiko")
private_key = paramiko.RSAKey.from_private_key_file(key_path)

# --- Device List ---
my_devices = [
    {
        "host": "192.168.1.4",
        "username": "USERNAME1",
        "port": 22,
        "name": "router1",
    },
    {
        "host": "192.168.1.5",
        "username": "USERNAME2",
        "port": 22,
        "name": "router2",
    },
]

# --- Report Setup ---
today = date.today().strftime("%Y-%m-%d")
REPORT_FILE = f"Audit_Report_{today}.txt"
report_lines = ["--- Network Device Audit Report ---\n"]

# --- Audit Each Device ---
for device in my_devices:
    client = None
    name = device["name"]
    host = device["host"]

    print(f"\nAttempting to connect to {host} via SSH...")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=device["port"], username=device["username"], pkey=private_key)
        print(f"Successfully connected to {host} via SSH")

        # Check 1: Enabled Telnet Access
        stdin, stdout, stderr = client.exec_command("show running-config | include telnet")
        telnet_output = stdout.read().decode()
        if "telnet" in telnet_output.lower():
            telnet_status = "Telnet is enabled"
        else:
            telnet_status = "Telnet is disabled"

        # Check 2: Enabled HTTP Server (insecure)
        stdin, stdout, stderr = client.exec_command("show running-config | include ip http server")
        http_output = stdout.read().decode()
        if "no ip http server" in http_output.lower():
            http_status = "HTTP server is disabled"
        elif "ip http server" in http_output.lower():
            http_status = "HTTP server is enabled"
        else:
            http_status = "HTTP server is disabled"

        # Check 3: Default SNMP Community Strings ("public" or "private")
        stdin, stdout, stderr = client.exec_command("show running-config | include snmp-server community")
        snmp_output = stdout.read().decode()
        if "public" in snmp_output.lower() or "private" in snmp_output.lower():
            snmp_status = "Default SNMP community strings found"
        else:
            snmp_status = "No default SNMP community strings found"

        # Append findings to report
        report_lines.append(f"Device: {name}")
        report_lines.append(f"    - Telnet Status: {telnet_status}")
        report_lines.append(f"    - HTTP Server Status: {http_status}")
        report_lines.append(f"    - SNMP Status: {snmp_status}\n")

    except paramiko.AuthenticationException:
        print(f"SSH authentication failed for {host}.")
        report_lines.append(f"Device: {name}")
        report_lines.append(f"    - Telnet Status: SSH authentication failed")
        report_lines.append(f"    - HTTP Server Status: SSH authentication failed")
        report_lines.append(f"    - SNMP Status: SSH authentication failed\n")

    except paramiko.SSHException as e:
        print(f"SSH error for {host}: {e}")
        report_lines.append(f"Device: {name}")
        report_lines.append(f"    - Telnet Status: SSH error: {e}")
        report_lines.append(f"    - HTTP Server Status: SSH error: {e}")
        report_lines.append(f"    - SNMP Status: SSH error: {e}\n")

    except Exception as e:
        print(f"Error connecting to {host}: {e}")
        report_lines.append(f"Device: {name}")
        report_lines.append(f"    - Telnet Status: Could not connect: {e}")
        report_lines.append(f"    - HTTP Server Status: Could not connect: {e}")
        report_lines.append(f"    - SNMP Status: Could not connect: {e}\n")

    finally:
        if client:
            client.close()
            print(f"Disconnected from {host}")

# --- Save Report ---
with open(REPORT_FILE, "w") as f:
    f.write("\n".join(report_lines))

print(f"\nAudit report saved to {REPORT_FILE}")