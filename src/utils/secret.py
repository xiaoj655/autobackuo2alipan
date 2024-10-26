import secrets

def generate_secret_key(length: int = 16):
    return secrets.token_hex(length)
