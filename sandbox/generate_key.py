import secrets

# Generate a random secret key
secret_key = secrets.token_hex(32)  # Generates a random 64-character hex string
print(secret_key)