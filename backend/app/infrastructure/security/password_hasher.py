from __future__ import annotations

import hashlib
import hmac
import os

from app.application.ports.password_hasher import PasswordHasher

_ITERATIONS = 210_000
_SCHEME = "pbkdf2_sha256"


class Pbkdf2PasswordHasher:
    def hash(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
        return f"{_SCHEME}${_ITERATIONS}${salt.hex()}${digest.hex()}"

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            scheme, iterations_raw, salt_hex, digest_hex = password_hash.split("$")
            if scheme != _SCHEME:
                return False
            iterations = int(iterations_raw)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
        except (ValueError, AttributeError):
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return hmac.compare_digest(actual, expected)


def get_password_hasher() -> PasswordHasher:
    return Pbkdf2PasswordHasher()
