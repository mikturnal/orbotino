import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from orbotino.core.crypto import TokenCipher, TokenDecryptionError


def make_key() -> SecretStr:
    return SecretStr(Fernet.generate_key().decode())


@pytest.fixture
def cipher() -> TokenCipher:
    return TokenCipher(make_key())


def test_encrypt_then_decrypt_returns_original(cipher: TokenCipher) -> None:
    text = "my-twitch-token"
    encrypted = cipher.encrypt(text)
    assert cipher.decrypt(encrypted) == text


def test_encrypted_text_differs_from_original(cipher: TokenCipher) -> None:
    text = "my-twitch-token"
    encrypted = cipher.encrypt(text)
    assert encrypted != text
    assert text not in encrypted


def test_wrong_key_raises_error(cipher: TokenCipher) -> None:
    encrypted = cipher.encrypt("my-twitch-token")
    other_cipher = TokenCipher(make_key())
    with pytest.raises(TokenDecryptionError):
        other_cipher.decrypt(encrypted)
