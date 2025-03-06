import secrets
import string
from itsdangerous import URLSafeTimedSerializer
def get_salt():
    # Generate a random token of 4 bytes
    token = secrets.token_bytes(4)
    # Define a custom character set, including symbols
    symbols = string.digits + "!@#$%^&*()-+"
    # Map the byte data to the custom set of symbols
    return ''.join(symbols[b % len(symbols)] for b in token)

def generate_verification_token(email, serialiser):
    return serialiser.dumps(email, salt='email-verification')

def verify_token(token, serialiser):
    try:
        email = serialiser.loads(token, salt='email-verification', max_age=3600)
        return email
    except:
        return None