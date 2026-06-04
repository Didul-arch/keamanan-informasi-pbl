from cryptography.fernet import Fernet
from backend.app.infrastructure.config.settings import settings

# Initialize Fernet cipher with the secret key from settings
# The key must be 32 url-safe base64-encoded bytes.
fernet = Fernet(settings.ENCRYPTION_KEY.encode('utf-8'))

def encrypt_string(data: str | None) -> str | None:
    """Encrypts a string and returns the url-safe base64 encoded cipher text string."""
    if not data:
        return None
    return fernet.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_string(encrypted_data: str | None) -> str | None:
    """Decrypts a url-safe base64 encoded cipher text string back to plain text."""
    if not encrypted_data:
        return None
    return fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypts raw bytes."""
    return fernet.encrypt(data)

def decrypt_bytes(encrypted_data: bytes) -> bytes:
    """Decrypts raw encrypted bytes."""
    return fernet.decrypt(encrypted_data)
