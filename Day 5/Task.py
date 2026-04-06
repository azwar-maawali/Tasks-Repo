import paramiko
import os

# 1- Device connection details
hostname = "10.0.2.15"
port = 22
username = "codeacademy"
key_path = os.path.expanduser("~/.ssh/id_rsa_paramiko")  # Private key path

# 2- Create an SSH client
client = None
client = paramiko.SSHClient()

# 3- Automatically add the server's host key
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # 4- Load the private key
    private_key = paramiko.RSAKey.from_private_key_file(key_path)

    # 5- Connect using the key (no password needed)
    client.connect(hostname, port=port, username=username, pkey=private_key)
    print(f"Connected to {hostname} using SSH key authentication")

    # 6- Run a command
    stdin, stdout, stderr = client.exec_command("show version")
    print(stdout.read().decode())

# 7- Exceptions
except paramiko.AuthenticationException:
    print("Authentication failed: check your key or username.")
except paramiko.SSHException as e:
    print(f"SSH error occurred: {e}")
except FileNotFoundError:
    print(f"Private key not found at: {key_path}")
except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    if client:
        client.close()
    print("Connection closed.")