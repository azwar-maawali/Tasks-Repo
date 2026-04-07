import os
from datetime import date
from netmiko import ConnectHandler

# ── Device List ───────────────────────────────────────────
my_devices = [
    {
        "device_type": "cisco_ios",
        "ip":          "192.168.1.1",
        "username":    "admin",
        "password":    "password",
        "port":        22,
    },
    {
        "device_type": "cisco_ios",
        "ip":          "192.168.1.2",
        "username":    "admin",
        "password":    "password",
        "port":        22,
    },
    {
        "device_type": "cisco_ios",
        "ip":          "10.0.0.1",
        "username":    "admin",
        "password":    "password",
        "port":        22,
    },
    {
        "device_type": "juniper_junos",
        "ip":          "192.168.1.3",
        "username":    "admin",
        "password":    "password",
        "port":        22,
    },
]

# ── Backup Directory ──────────────────────────────────────
BACKUP_DIR = "./backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

# ── Loop Through Each Device ──────────────────────────────
for device in my_devices:

    net_connect = None

    print(f"\nAttempting to connect to {device['ip']} ({device['device_type']})...")

    try:
        # ── Connect ───────────────────────────────────────
        net_connect = ConnectHandler(**device)
        print(f"Successfully connected to {device['ip']}.")

        # ── Get Hostname ──────────────────────────────────
        hostname = net_connect.find_prompt().strip().replace("#", "").replace(">", "")
        print(f"Device Hostname: {hostname}")

        # ── Get Current Date ──────────────────────────────
        today = date.today().strftime("%Y-%m-%d")

        # ── Construct Filename & Path ─────────────────────
        filename = f"{hostname}_{today}.txt"
        filepath = os.path.join(BACKUP_DIR, filename)

        # ── Retrieve Running Config ───────────────────────
        print(f"Retrieving running configuration from {hostname}...")
        config = net_connect.send_command("show running-config")

        # ── Save to File ──────────────────────────────────
        with open(filepath, "w") as f:
            f.write(config)

        print(f"Configuration backup for {hostname} saved to {filepath} successfully.")

    except Exception as e:
        print(f"Error backing up configuration for {device['ip']}: {e}")

    finally:
        if "net_connect" in locals() and net_connect.is_alive():
            net_connect.disconnect()
        print(f"Disconnected from {device['ip']}.")