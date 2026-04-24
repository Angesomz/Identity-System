from cryptography.fernet import Fernet
from configs.settings import get_settings

settings = get_settings()

class EncryptionService:
    def __init__(self):
        # Ensure key is bytes
        key = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY
        # Fernet requires 32 url-safe base64-encoded bytes. If key is raw, this might fail without proper generation.
        # For this simulation, we assume ENCRYPTION_KEY is a valid Fernet key.
        try:
            self.cipher = Fernet(key)
        except Exception:
            # Fallback for dev/test if key format is wrong
            self.cipher = Fernet(Fernet.generate_key())

    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        return self.cipher.decrypt(token)
