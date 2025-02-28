import secrets
import string

def get_salt():
    # Generate a random token of 4 bytes
    token = secrets.token_bytes(4)
    # Define a custom character set, including symbols
    symbols = string.digits + "!@#$%^&*()-+"
    # Map the byte data to the custom set of symbols
    return ''.join(symbols[b % len(symbols)] for b in token)

