# subnet_calculator.py
import ipaddress

ip_input = input("Enter an IP address (e.g., 192.168.1.1): ")
cidr_input = input("Enter CIDR prefix (e.g., 24): ")

print("\n--- Subnet Calculator ---")

try:
    cidr = int(cidr_input)
    network = ipaddress.IPv4Network(f"{ip_input}/{cidr}", strict=False)

    print(f"Network Address:       {network.network_address}")
    print(f"Broadcast Address:     {network.broadcast_address}")
    print(f"Number of Usable Hosts: {network.num_addresses - 2}")

except ValueError as e:
    print(f"Error: Invalid IP address or CIDR prefix provided. Details: {e}")

print("-------------------------")