# ip_validator.py

def validate_ip(ip):
    parts = ip.split(".")
    is_valid = True

    if len(parts) != 4:
        is_valid = False
    else:
        for part in parts:
            if not part.isdigit():
                is_valid = False
                break
            if not (0 <= int(part) <= 255):
                is_valid = False
                break

    return is_valid


# Main program
print("Enter IPv4 addresses one per line.")
print("Press Enter on a blank line when done.\n")

results = []

while True:
    ip = input("Enter an IPv4 address: ")
    
    # Stop if blank line
    if ip == "":
        break
    
    if validate_ip(ip):
        results.append((ip, "✅ Valid"))
    else:
        results.append((ip, "❌ Invalid"))

# Summary
print("\n--- Summary ---")
for ip, status in results:
    print(f"{status} : {ip}")

print(f"\nTotal entered : {len(results)}")
print(f"Valid         : {sum(1 for _, s in results if '✅' in s)}")
print(f"Invalid       : {sum(1 for _, s in results if '❌' in s)}")