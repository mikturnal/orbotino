from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr


class TokenDecryptionError(Exception):
    """Exception raised when invalid token or damaged data"""


class TokenCipher:
    def __init__(self, key: SecretStr) -> None:
        self._fernet = Fernet(key.get_secret_value())

    def encrypt(self, plaintext: str) -> str:
        encrypted = self._fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, token: str) -> str:
        try:
            decrypted = self._fernet.decrypt(token.encode())
        except InvalidToken as e:
            raise TokenDecryptionError(
                "Stored token can't be decrypted. Did TOKEN_ENCRYPTION_KEY change?"
            ) from e
        return decrypted.decode()
