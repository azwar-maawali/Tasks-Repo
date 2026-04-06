# ip_validator.py

ip = input("Enter an IPv4 address: ")

parts = ip.split(".")
is_valid = True

# Must have exactly 4 octets
if len(parts) != 4:
    is_valid = False
else:
    for part in parts:
        # Each octet must be digits only
        if not part.isdigit():
            is_valid = False
            break
        # Each octet must be between 0 and 255
        if not (0 <= int(part) <= 255):
            is_valid = False
            break

if is_valid:
    print(f"✅ '{ip}' is a valid IPv4 address.")
else:
    print(f"❌ '{ip}' is NOT a valid IPv4 address.")